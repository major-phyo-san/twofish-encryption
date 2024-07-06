import base64
import psutil
import time
import tracemalloc

from PyQt6.QtWidgets import QLabel, QVBoxLayout, QHBoxLayout, QWidget, QPushButton, QMessageBox, QFileDialog, QTextEdit
from PyQt6.QtCore import Qt

from twofish import Twofish

from helpers.helpers import pad, convert_to_bytes, convert_to_b64str

class EncryptionPage(QWidget):
    def __init__(self,stack):
        super().__init__()

        self.stack = stack

        pageLabel = QLabel("Twofish Encryption")
        pageLabel.setStyleSheet("font-size: 24px; padding: 10px;")

        # Create and configure file picker buttons
        self.keyfile_button = QPushButton("Select Towfish key file")
        self.keyfile_button.setFixedWidth(150)  # Set fixed width
        self.keyfile_button.setFixedHeight(40)  # Set fixed height
        self.keyfile_button.clicked.connect(lambda: self.pick_key_file())
        self.keyfile_label = QLabel("No file selected")

        self.textfile_button = QPushButton("Select plain text file")
        self.textfile_button.setFixedWidth(150)  # Set fixed width
        self.textfile_button.setFixedHeight(40)  # Set fixed height
        self.textfile_button.clicked.connect(lambda: self.pick_text_file())
        self.textfile_label = QLabel("No file selected")

        # Layout for file picker 1
        file1_layout = QHBoxLayout()
        file1_layout.addStretch()
        file1_layout.addWidget(self.keyfile_button)
        file1_layout.addWidget(self.keyfile_label)
        file1_layout.addStretch()

        # Layout for file picker 2
        file2_layout = QHBoxLayout()
        file2_layout.addStretch()
        file2_layout.addWidget(self.textfile_button)
        file2_layout.addWidget(self.textfile_label)
        file2_layout.addStretch()

        self.analysis_output_label = QLabel("Computational Analysis:")
        self.analysis_output = QTextEdit()
        # self.analysis_output.setFixedWidth(120)  # Set fixed width
        self.analysis_output.setFixedHeight(180)  # Set fixed height
        self.analysis_output.setReadOnly(True)
        self.analysis_output.setStyleSheet("font-size: 24px; padding: 5px; height: 50px;")

        # Create and configure the "Confirm" button
        encrypt_button = QPushButton("Encrypt")
        encrypt_button.setStyleSheet("font-size: 18px; padding: 10px;")
        encrypt_button.clicked.connect(self.encrypt_btn_clicked)

        # Create and configure the "Save As" button
        save_button = QPushButton("Save As")
        save_button.setStyleSheet("font-size: 18px; padding: 10px;")
        save_button.clicked.connect(self.save_to_file)

        # Layout for buttons
        button_layout = QHBoxLayout()
        button_layout.addWidget(encrypt_button)
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
        self.textfile_path = None
        self.cipherText = None

    def go_back(self):
        self.analysis_output.setPlainText("")
        self.keyfile_path = None
        self.textfile_path = None
        self.cipherText = None
        self.stack.setCurrentIndex(0)

    def pick_key_file(self):        
        file_path, _ = QFileDialog.getOpenFileName(self, "Select Key File", "", "Twofish Key Files (*.tfk);;All Files (*)")
        if file_path:
            self.keyfile_path = file_path
            self.keyfile_label.setText(f"Key file selected")

    def pick_text_file(self):
        file_path, _ = QFileDialog.getOpenFileName(self, "Select Text File", "", "Text Files (*.txt);;All Files (*)")
        if file_path:
            self.textfile_path = file_path
            self.textfile_label.setText(f"Text file selected")

    def encrypt_btn_clicked(self):
        # Ensure both files are selected
        if not self.keyfile_path or not self.textfile_path:
            QMessageBox.warning(self, "Warning", "Please select both key and text files before encryption.")
            return

        try:
            # Read contents of both files
            with open(self.keyfile_path, 'r') as file1, open(self.textfile_path, 'r') as file2:
                base64_string = file1.read()
                plainText = file2.read()
                if base64_string and plainText:
                    QMessageBox.information(self, "Info", "Starting encryption.")
                    key = convert_to_bytes(base64_string)
                    tracemalloc.start()
                    start_time = time.time()
                    self.cipherText = self.encrypt(key, plainText)
                    end_time = time.time()
                    current, peak = tracemalloc.get_traced_memory()
                    time_taken_ms = (end_time - start_time) * 1000
                    cpu_usage, memory_usage = self.monitor_resources()
                    timeTakenAnalysis = f"Time taken: {time_taken_ms:.2f} ms"
                    cpuUsageAnalysis = f"CPU usage: {cpu_usage}%"        
                    memoryUsageAnalysis = f"Memory usage: {peak / 10**3} KB"
                    combinedAnalysis = f"{timeTakenAnalysis}\n{cpuUsageAnalysis}\n{memoryUsageAnalysis}"
                    self.analysis_output.setPlainText(combinedAnalysis)                    
                    if self.cipherText:
                        QMessageBox.information(self, "Success", "Encryption done.")
                    else:
                        QMessageBox.critical(self, "Error", "Encryption failed.")                
        except Exception as e:
            errMsg = "Encryption failed: %s " %e
            QMessageBox.critical(self, "Error", errMsg)                
    
    def encrypt(self, key, plainText):
        cipher = Twofish(key)
        cipherText = None
        plain_text_bytes = plainText.encode()
        padded_data = pad(plain_text_bytes, 16)
        encrypted_data = b""
        try:
            for i in range(0, len(padded_data), 16):
                block = padded_data[i:i + 16]
                encrypted_data += cipher.encrypt(block)
        except Exception as e:
            cipherText = None
            errMsg = "Encryption failed: %s " %e
            QMessageBox.critical(self, "Error", errMsg)
        if encrypted_data:
            cipherText = convert_to_b64str(encrypted_data)
        return cipherText

    def save_to_file(self):
        if not self.cipherText:
            QMessageBox.warning(self, "Warning", "No cipher text to save. Check the encryption first.")
            return

        # Open file dialog to save the combined content
        file_path, _ = QFileDialog.getSaveFileName(self, "Save File", "", "Text Files (*.txt);;All Files (*)")
        if file_path:
            try:
                # Write the combined content to the selected file
                with open(file_path, 'w') as file:
                    file.write(self.cipherText)
                QMessageBox.information(self, "Success", "Cipher text file saved successfully.")
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to save cipher text file: {e}")
                
    def monitor_resources(self, interval=1):
        cpu_usage = psutil.cpu_percent(interval=interval)
        memory_info = psutil.virtual_memory()
        return cpu_usage, memory_info.percent