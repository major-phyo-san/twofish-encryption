import sys
from PyQt6.QtWidgets import QApplication, QLabel, QPushButton, QVBoxLayout, QHBoxLayout, QWidget, QFileDialog, QMessageBox

class MainWindow(QWidget):
    def __init__(self):
        super().__init__()

        # Set window properties
        self.setWindowTitle("File Picker Example")
        self.setGeometry(100, 100, 500, 300)

        # Create and configure file picker buttons
        self.file1_button = QPushButton("Select File 1")
        self.file1_button.clicked.connect(lambda: self.pick_file(1))
        self.file1_label = QLabel("No file selected")

        self.file2_button = QPushButton("Select File 2")
        self.file2_button.clicked.connect(lambda: self.pick_file(2))
        self.file2_label = QLabel("No file selected")

        # Create and configure the "Confirm" button
        confirm_button = QPushButton("Confirm")
        confirm_button.clicked.connect(self.confirm_selection)
        confirm_button.setStyleSheet("font-size: 18px; padding: 10px;")

        # Create and configure the "Save As" button
        save_button = QPushButton("Save As")
        save_button.clicked.connect(self.save_to_file)
        save_button.setStyleSheet("font-size: 18px; padding: 10px;")

        # Layout for file pickers
        file_layout = QVBoxLayout()
        file_layout.addWidget(self.file1_button)
        file_layout.addWidget(self.file1_label)
        file_layout.addWidget(self.file2_button)
        file_layout.addWidget(self.file2_label)

        # Layout for buttons
        button_layout = QHBoxLayout()
        button_layout.addWidget(confirm_button)
        button_layout.addWidget(save_button)
        button_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        # Main layout
        main_layout = QVBoxLayout()
        main_layout.addLayout(file_layout)
        main_layout.addLayout(button_layout)

        # Set main layout
        self.setLayout(main_layout)

        # File paths storage
        self.file1_path = None
        self.file2_path = None
        self.combined_content = None

    def pick_file(self, file_number):
        # Open file dialog to select a file
        file_path, _ = QFileDialog.getOpenFileName(self, "Select File", "", "All Files (*)")
        if file_path:
            if file_number == 1:
                self.file1_path = file_path
                self.file1_label.setText(f"File 1: {file_path}")
            elif file_number == 2:
                self.file2_path = file_path
                self.file2_label.setText(f"File 2: {file_path}")

    def confirm_selection(self):
        # Ensure both files are selected
        if not self.file1_path or not self.file2_path:
            QMessageBox.warning(self, "Warning", "Please select both files before confirming.")
            return

        try:
            # Read contents of both files
            with open(self.file1_path, 'r') as file1, open(self.file2_path, 'r') as file2:
                content1 = file1.read()
                content2 = file2.read()
                # Combine the contents
                self.combined_content = content1 + "\n" + content2
                QMessageBox.information(self, "Success", "Files successfully combined.")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to combine files: {e}")

    def save_to_file(self):
        if not self.combined_content:
            QMessageBox.warning(self, "Warning", "No content to save. Confirm file selection first.")
            return

        # Open file dialog to save the combined content
        file_path, _ = QFileDialog.getSaveFileName(self, "Save File", "", "Text Files (*.txt);;All Files (*)")
        if file_path:
            try:
                # Write the combined content to the selected file
                with open(file_path, 'w') as file:
                    file.write(self.combined_content)
                QMessageBox.information(self, "Success", "File saved successfully.")
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to save file: {e}")

def main():
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
