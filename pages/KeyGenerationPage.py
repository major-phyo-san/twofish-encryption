import base64

from Crypto.Random import get_random_bytes

from PyQt6.QtWidgets import QLabel, QVBoxLayout, QHBoxLayout, QWidget, QPushButton, QTextEdit, QMessageBox, QComboBox, QFileDialog
from PyQt6.QtCore import Qt

from helpers.helpers import convert_to_b64str

class KeyGenerationPage(QWidget):
    def __init__(self,stack):
        super().__init__()

        self.stack = stack

        pageLabel = QLabel("Key Generation")
        pageLabel.setStyleSheet("font-size: 24px; padding: 10px;")

        # Create and configure select box
        self.options = {
            "128 Bit": 128,
            "192 Bit": 192,
            "256 Bit": 256
        }
        self.select_box = QComboBox()
        self.select_box.addItems(self.options.keys())
        self.select_box.setStyleSheet("font-size: 18px; padding: 5px;")

        # Create and configure text box for displaying the generated value
        self.text_box = QTextEdit()
        self.text_box.setReadOnly(True)
        self.text_box.setFixedHeight(300)
        self.text_box.setStyleSheet("font-size: 18px; padding: 5px; height: 20px;")

        # Create and configure the "Confirm" button
        self.confirm_button = QPushButton("Confirm")
        self.confirm_button.setStyleSheet("font-size: 18px; padding: 10px; width: 50px;")
        self.confirm_button.clicked.connect(self.confirm_selection)

        # Create and configure the "Save As" button
        self.save_button = QPushButton("Save Key")
        self.save_button.setStyleSheet("font-size: 18px; padding: 10px;")
        self.save_button.clicked.connect(self.save_to_file)

        back_button = QPushButton("Back")
        back_button.setStyleSheet("font-size: 18px; padding: 10px;")
        back_button.clicked.connect(self.go_back)

        # Layout for buttons
        self.button_layout = QHBoxLayout()
        self.button_layout.addWidget(self.save_button)
        self.button_layout.addWidget(back_button)
        self.button_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)       

        # Main layout
        layout = QVBoxLayout()
        layout.addWidget(pageLabel)

        layout.addWidget(QLabel("Select key size:"))
        layout.addWidget(self.select_box)

        layout.addWidget(self.confirm_button)

        layout.addWidget(QLabel("Generated key:"))
        layout.addWidget(self.text_box)

        layout.addLayout(self.button_layout)
        layout.setAlignment(pageLabel, Qt.AlignmentFlag.AlignCenter)

        self.setLayout(layout)

    def go_back(self):
        self.text_box.setPlainText("")
        self.stack.setCurrentIndex(0)

    def confirm_selection(self):
        selected_label = self.select_box.currentText()
        key_size = self.options.get(selected_label, "")
        # Generate key based on the selection
        generated_key = self.generate_key(key_size)
        self.text_box.setPlainText(generated_key)
    
    def generate_key(self, key_size):
        # Generate a key from the key_size and returns as base64 string
        # key_size is in number of bits, (128, 192 and 256 in this case)
        key_size = int(key_size / 8)
        key = get_random_bytes(key_size)
        base64_string = convert_to_b64str(key)
        return base64_string

    def save_to_file(self):
        # Get the generated value from the text box
        text = self.text_box.toPlainText()
        if not text:
            # If no text is generated, show a warning message
            QMessageBox.warning(self, "Warning", "No value to save.")
            return
        # Open file dialog to save the file
        file_path, _ = QFileDialog.getSaveFileName(self, "Save File", "", "Twofish Key Files (*.tfk);;All Files (*)")
        if file_path:
            try:
                # Write the text to the selected file
                with open(file_path, 'w') as file:
                    file.write(text)
                QMessageBox.information(self, "Success", "Key file saved successfully.")
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to key save file: {e}")