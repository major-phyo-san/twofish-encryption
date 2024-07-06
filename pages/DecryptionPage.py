import base64
import psutil
import time
import tracemalloc

from PyQt6.QtWidgets import QLabel, QVBoxLayout, QHBoxLayout, QWidget, QPushButton, QMessageBox, QFileDialog, QTextEdit
from PyQt6.QtCore import Qt

from twofish import Twofish

from helpers.helpers import unpad, convert_to_bytes, convert_to_b64str, convert_to_str

class DecryptionPage(QWidget):
    def __init__(self,stack):
        super().__init__()

        self.stack = stack

        pageLabel = QLabel("Twofish Decryption")
        pageLabel.setStyleSheet("font-size: 24px; padding: 10px;")

        # Create and configure file picker buttons
        self.keyfile_button = QPushButton("Select Towfish key file")
        self.keyfile_button.setFixedWidth(150)  # Set fixed width
        self.keyfile_button.setFixedHeight(40)  # Set fixed height
        self.keyfile_button.clicked.connect(lambda: self.pick_key_file())
        self.keyfile_label = QLabel("No file selected")

        self.cipherTextFile_button = QPushButton("Select cipher text file")
        self.cipherTextFile_button.setFixedWidth(150)  # Set fixed width
        self.cipherTextFile_button.setFixedHeight(40)  # Set fixed height
        self.cipherTextFile_button.clicked.connect(lambda: self.pick_text_file())
        self.cipherTextFile_label = QLabel("No file selected")

        # Layout for file picker 1
        file1_layout = QHBoxLayout()
        file1_layout.addStretch()
        file1_layout.addWidget(self.keyfile_button)
        file1_layout.addWidget(self.keyfile_label)
        file1_layout.addStretch()

        # Layout for file picker 2
        file2_layout = QHBoxLayout()
        file2_layout.addStretch()
        file2_layout.addWidget(self.cipherTextFile_button)
        file2_layout.addWidget(self.cipherTextFile_label)
        file2_layout.addStretch()

        self.analysis_output_label = QLabel("Computational Analysis:")
        self.analysis_output = QTextEdit()
        # self.analysis_output.setFixedWidth(120)  # Set fixed width
        self.analysis_output.setFixedHeight(180)  # Set fixed height
        self.analysis_output.setReadOnly(True)
        self.analysis_output.setStyleSheet("font-size: 24px; padding: 5px; height: 50px;")

        # Create and configure the "Confirm" button
        decrypt_button = QPushButton("Decrypt")
        decrypt_button.setStyleSheet("font-size: 18px; padding: 10px;")
        decrypt_button.clicked.connect(self.decrypt_btn_clicked)

        # Create and configure the "Save As" button
        save_button = QPushButton("Save As")
        save_button.setStyleSheet("font-size: 18px; padding: 10px;")
        save_button.clicked.connect(self.save_to_file)

        # Layout for buttons
        button_layout = QHBoxLayout()
        button_layout.addWidget(decrypt_button)
        button_layout.addWidget(save_button)
        button_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        back_button = QPushButton("Back")
        back_button.setStyleSheet("font-size: 18px; padding: 10px;")
        back_button.clicked.connect(self.go_back)

        layout = QVBoxLayout()
        layout.addWidget(pageLabel)
        layout.addLayout(file1_layout)
        layout.addLayout(file2_layout)
        layout.addWidget(self.analysis_output_label)
        layout.addWidget(self.analysis_output)
        layout.addLayout(button_layout)
        layout.addWidget(back_button)
        layout.setAlignment(pageLabel, Qt.AlignmentFlag.AlignCenter)
        layout.setAlignment(back_button, Qt.AlignmentFlag.AlignCenter)

        self.setLayout(layout)

         # File paths storage
        self.keyfile_path = None
        self.cipherTextFile_path = None
        self.plainText = None

    def go_back(self):
        self.analysis_output.setPlainText("")
        self.keyfile_path = None
        self.cipherTextFile_path = None
        self.plainText = None
        self.stack.setCurrentIndex(0)

    def pick_key_file(self):        
        file_path, _ = QFileDialog.getOpenFileName(self, "Select Key File", "", "Twofish Key Files (*.tfk);;All Files (*)")
        if file_path:
            self.keyfile_path = file_path
            self.keyfile_label.setText(f"Key file selected")

    def pick_text_file(self):
        file_path, _ = QFileDialog.getOpenFileName(self, "Select Cipher Text File", "", "Text Files (*.txt);;All Files (*)")
        if file_path:
            self.cipherTextFile_path = file_path
            self.cipherTextFile_label.setText(f"Cipher Text file selected")

    def decrypt_btn_clicked(self):
        # Ensure both files are selected
        if not self.keyfile_path or not self.cipherTextFile_path:
            QMessageBox.warning(self, "Warning", "Please select both key and cipher text files before decryption.")
            return

        try:
            # Read contents of both files
            with open(self.keyfile_path, 'r') as file1, open(self.cipherTextFile_path, 'r') as file2:
                base64_string = file1.read()
                cipherText = file2.read()
                if base64_string and cipherText:
                    QMessageBox.information(self, "Info", "Starting decryption.")
                    key = convert_to_bytes(base64_string)
                    tracemalloc.start()
                    start_time = time.time()
                    self.plainText = self.decrypt(key, cipherText)
                    end_time = time.time()
                    current, peak = tracemalloc.get_traced_memory()
                    time_taken_ms = (end_time - start_time) * 1000
                    cpu_usage, memory_usage = self.monitor_resources()
                    timeTakenAnalysis = f"Time taken: {time_taken_ms:.2f} ms"
                    cpuUsageAnalysis = f"CPU usage: {cpu_usage}%"        
                    memoryUsageAnalysis = f"Memory usage: {peak / 10**3} KB"
                    combinedAnalysis = f"{timeTakenAnalysis}\n{cpuUsageAnalysis}\n{memoryUsageAnalysis}"
                    self.analysis_output.setPlainText(combinedAnalysis)                    
                    if self.plainText:
                        QMessageBox.information(self, "Success", "Decryption done.")
                    else:
                        QMessageBox.critical(self, "Error", "Decryption failed.")                
        except Exception as e:
            errMsg = "Decryption failed: %s " %e
            QMessageBox.critical(self, "Error", errMsg)                
    
    def decrypt(self, key, cipherText):        
        cipher = Twofish(key)
        plainText = None
        cipher_text_bytes = convert_to_bytes(cipherText)
        decrypted_padded_data = b""
        try:
            for i in range(0, len(cipher_text_bytes), 16):
                block = cipher_text_bytes[i:i + 16]
                decrypted_padded_data += cipher.decrypt(block)
            decrypted_data = unpad(decrypted_padded_data, 16)
        except Exception as e:
            print(e)
            errMsg = "Decryption failed: %s " %e
            QMessageBox.critical(self, "Error", errMsg)
        
        if decrypted_data:            
            plainText = convert_to_str(decrypted_data)
            return plainText

    def save_to_file(self):
        if not self.plainText:
            QMessageBox.warning(self, "Warning", "No plain text to save. Check the decryption first.")
            return

        # Open file dialog to save the combined content
        file_path, _ = QFileDialog.getSaveFileName(self, "Save File", "", "Text Files (*.txt);;All Files (*)")
        if file_path:
            try:
                # Write the combined content to the selected file
                with open(file_path, 'w') as file:
                    file.write(self.plainText)
                QMessageBox.information(self, "Success", "Plain text file saved successfully.")
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to save plain text file: {e}")
                
    def monitor_resources(self, interval=1):
        cpu_usage = psutil.cpu_percent(interval=interval)
        memory_info = psutil.virtual_memory()
        return cpu_usage, memory_info.percent