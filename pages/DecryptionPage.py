import os
import psutil
import time
import tracemalloc

from Crypto.Random import get_random_bytes

from PyQt6.QtWidgets import QLabel, QVBoxLayout, QHBoxLayout, QWidget, QPushButton, QMessageBox, QFileDialog, QTextEdit
from PyQt6.QtCore import Qt

from twofish import Twofish

from helpers.helpers import unpad, convert_to_bytes, convert_to_b64str, convert_to_str, convert_string_to_key, generate_random_string

class DecryptionPage(QWidget):
    def __init__(self,stack):
        super().__init__()

        self.stack = stack

        pageLabel = QLabel("Twofish Decryption")
        pageLabel.setStyleSheet("font-size: 24px; padding: 10px;")

        self.keystring_input = QTextEdit()        
        self.keystring_input.setFixedHeight(50)
        self.keystring_input.setPlaceholderText("Input 16-character key")
        self.keystring_input.setStyleSheet("font-size: 18px; padding: 5px; height: 20px;")

        # Create and configure file picker buttons
        self.cipherTextFile_button = QPushButton("Select cipher text file")
        self.cipherTextFile_button.setFixedWidth(150)  # Set fixed width
        self.cipherTextFile_button.setFixedHeight(40)  # Set fixed height
        self.cipherTextFile_button.clicked.connect(lambda: self.pick_text_file())
        self.cipherTextFile_label = QLabel("No file selected")

        # Layout for file picker 1
        file1_layout = QHBoxLayout()
        file1_layout.addStretch()
        file1_layout.addStretch()

        # Layout for file picker 2
        file2_layout = QHBoxLayout()
        file2_layout.addStretch()
        file2_layout.addWidget(self.cipherTextFile_button)
        file2_layout.addWidget(self.cipherTextFile_label)
        file2_layout.addStretch()

        self.file_content_label = QLabel("File Contents:")
        self.file_content = QTextEdit()
        # self.analysis_output.setFixedWidth(120)  # Set fixed width
        self.file_content.setFixedHeight(100)  # Set fixed height
        self.file_content.setReadOnly(True)

        self.output_content_label = QLabel("Output text:")
        self.output_content = QTextEdit()
        # self.analysis_output.setFixedWidth(120)  # Set fixed width
        self.output_content.setFixedHeight(100)  # Set fixed height
        self.output_content.setReadOnly(True)

        self.analysis_output_label = QLabel("Computational Analysis:")
        self.analysis_output = QTextEdit()
        # self.analysis_output.setFixedWidth(120)  # Set fixed width
        self.analysis_output.setFixedHeight(50)  # Set fixed height
        self.analysis_output.setReadOnly(True)
        # self.analysis_output.setStyleSheet("font-size: 24px; padding: 5px; height: 50px;")

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
        layout.addWidget(self.keystring_input)
        layout.addLayout(file2_layout)
        layout.addWidget(self.file_content_label)
        layout.addWidget(self.file_content)
        layout.addWidget(self.output_content_label)
        layout.addWidget(self.output_content)
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
        self.keystring_input.setPlainText(None)
        self.file_content.setPlainText(None)
        self.output_content.setPlainText(None)
        self.analysis_output.setPlainText("")
        self.cipherTextFile_label.setText("No file selected")
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
            file_size = os.stat(file_path).st_size/1024
            self.cipherTextFile_path = file_path
            self.cipherTextFile_label.setText(f"Cipher Text file selected, file size {file_size:.2f} KB")
            try:
                with open(self.cipherTextFile_path, 'r') as cipherTextfile:
                    cipherText = cipherTextfile.read()
                    if cipherText:
                        self.file_content.setPlainText(cipherText)
            except Exception as e:
                errMsg = "Opening cipher text file failed: %s " %e
                QMessageBox.critical(self, "Error", errMsg)

    def decrypt_btn_clicked(self):
        # Ensure both files are selected
        keystring = self.keystring_input.toPlainText()
        if len(keystring) != 16:
            QMessageBox.warning(self, "Warning", "Key must be exactly 16 characters")
            return
        if not self.cipherTextFile_path:
            QMessageBox.warning(self, "Warning", "Please select both cipher text file before decryption.")
            return

        try:
            # Read contents of both files
            with open(self.cipherTextFile_path, 'r') as file2:
                base64_string = convert_string_to_key(keystring)
                # base64_string = file1.read()
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
                    combinedAnalysis = f"{timeTakenAnalysis}"                    
                    if self.plainText:
                        QMessageBox.information(self, "Success", "Decryption done.")
                        self.output_content.setPlainText(self.plainText)
                        self.analysis_output.setPlainText(combinedAnalysis)                    
                    else:
                        QMessageBox.critical(self, "Error", "Decryption failed.")                
        except Exception as e:
            errMsg = "Decryption failed: %s " %e
            QMessageBox.critical(self, "Error", errMsg)
    
    def decrypt(self, key, cipherText):     
        decrypted_data = None   
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
            errMsg = "Decryption failed: password not correct "
            QMessageBox.critical(self, "Error", errMsg)
        
        if decrypted_data:     
            try:       
                plainText = convert_to_str(decrypted_data)
                return plainText
            except Exception as e:
                QMessageBox.critical(self, "Error", "Decryption failed, ciphertext corrupted.")
                print("Error, decryption failed, ciphertext corrupted.")
                # random_bytes = get_random_bytes(len(cipher_text_bytes))
                # random_base64_string = convert_to_b64str(decrypted_data)
                # plainText = random_base64_string
                plainText = generate_random_string(len(decrypted_data))
                # plainText = convert_to_b64str(decrypted_data) # convert corrupted decrypted datat to b64 str
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