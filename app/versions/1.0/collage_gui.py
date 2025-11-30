# collage_gui.py
from PySide6.QtWidgets import (
    QApplication, QWidget, QLabel, QLineEdit, QPushButton, QFileDialog,
    QVBoxLayout, QHBoxLayout, QMessageBox, QSpacerItem, QSizePolicy
)
from PySide6.QtGui import QFont
from PySide6.QtCore import Qt
from make_rectpack_collage import create_collage, parse_color
import sys
import os

# Default values
DEFAULTS = {
    "width": 2560,
    "height": 1440,
    "bgcolor": "transparent",
    "max_rotation": 5,
    "overlap_factor": 0.05,
    "rows": 0,
    "iterations": 15,
    "output_file": "collage.png"
}

# Default Documents folder
DEFAULT_FOLDER = os.path.join(os.path.expanduser("~"), "Documents")

class CollageApp(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Mike's Collage 1.0")
        self.setup_ui()

    def setup_ui(self):
        layout = QVBoxLayout()
        layout.setContentsMargins(15, 10, 15, 10)
        layout.setSpacing(10)

        layout.addSpacerItem(QSpacerItem(0, 5, QSizePolicy.Minimum, QSizePolicy.Fixed))

        # App title
        title = QLabel("Mike's Collage")
        title.setFont(QFont("Arial", 64, QFont.Bold))
        title.setStyleSheet("color: #62c6ff;")  # Blau
        title.setAlignment(Qt.AlignCenter)
        layout.addWidget(title)

        layout.addSpacerItem(QSpacerItem(0, 5, QSizePolicy.Minimum, QSizePolicy.Fixed))

        # Input folder
        self.input_folder_edit = self.add_labeled_folder(layout, "Input Folder", DEFAULT_FOLDER)

        # Output folder
        self.output_folder_edit = self.add_labeled_folder(layout, "Output Folder", DEFAULT_FOLDER)

        # Output file
        self.output_file_edit = self.add_labeled_input(layout, "Output File", DEFAULTS["output_file"])

        # Other parameters
        self.width_edit = self.add_labeled_input(layout, "Collage Width", str(DEFAULTS["width"]))
        self.height_edit = self.add_labeled_input(layout, "Collage Height", str(DEFAULTS["height"]))
        self.bgcolor_edit = self.add_labeled_input(layout, "Background Color", DEFAULTS["bgcolor"])
        self.max_rotation_edit = self.add_labeled_input(layout, "Max Rotation", str(DEFAULTS["max_rotation"]))
        self.overlap_edit = self.add_labeled_input(layout, "Overlap Factor", str(DEFAULTS["overlap_factor"]))
        self.rows_edit = self.add_labeled_input(layout, "Rows (0=auto)", str(DEFAULTS["rows"]))
        self.iterations_edit = self.add_labeled_input(layout, "Iterations", str(DEFAULTS["iterations"]))

        # Spacer zwischen Feldern und Buttons
        layout.addSpacerItem(QSpacerItem(0, 10, QSizePolicy.Minimum, QSizePolicy.Fixed)) # QSizePolicy.Expanding

        # Run / Exit buttons
        hbox_buttons = QHBoxLayout()
        run_btn = QPushButton("Run")
        run_btn.clicked.connect(self.run_collage)
        exit_btn = QPushButton("Exit")
        exit_btn.clicked.connect(self.close)
        for btn in (run_btn, exit_btn):
            btn.setStyleSheet("""
                QPushButton {
                    padding: 8px 16px;
                    border-radius: 6px;
                    background-color: #3399ff;
                    color: white;
                }
                QPushButton:hover {
                    background-color: #55aaff;
                }
            """)
        hbox_buttons.addWidget(run_btn)
        hbox_buttons.addWidget(exit_btn)
        layout.addLayout(hbox_buttons)

        layout.addSpacerItem(QSpacerItem(0, 6, QSizePolicy.Minimum, QSizePolicy.Fixed))

        self.setLayout(layout)

    def add_labeled_input(self, parent_layout, label_text, default_value):
        hbox = QHBoxLayout()
        label = QLabel(label_text)
        label.setFixedWidth(120)
        hbox.addWidget(label)
        edit = QLineEdit(default_value)
        edit.setStyleSheet("""
            QLineEdit {
                padding: 6px;
                border-radius: 6px;
                background-color: #222222;
                color: white;
            }
        """)
        hbox.addWidget(edit)
        parent_layout.addLayout(hbox)
        return edit

    def add_labeled_folder(self, parent_layout, label_text, default_path):
        hbox = QHBoxLayout()
        label = QLabel(label_text)
        label.setFixedWidth(120)
        hbox.addWidget(label)
        edit = QLineEdit(default_path)
        edit.setStyleSheet("""
            QLineEdit {
                padding: 6px;
                border-radius: 6px;
                background-color: #222222;
                color: white;
            }
        """)
        hbox.addWidget(edit)
        browse_btn = QPushButton("Browse")
        browse_btn.setStyleSheet("""
            QPushButton {
                padding: 6px 12px;
                border-radius: 6px;
                background-color: #3399ff;
                color: white;
            }
            QPushButton:hover {
                background-color: #55aaff;
            }
        """)
        browse_btn.clicked.connect(lambda _, e=edit: self.browse_folder(e))
        hbox.addWidget(browse_btn)
        parent_layout.addLayout(hbox)
        return edit

    def browse_folder(self, edit_widget):
        folder = QFileDialog.getExistingDirectory(self, "Select Folder", edit_widget.text())
        if folder:
            edit_widget.setText(folder)

    def run_collage(self):
        input_dir = self.input_folder_edit.text().strip()
        output_dir = self.output_folder_edit.text().strip()
        output_file = self.output_file_edit.text().strip()

        if not input_dir:
            QMessageBox.warning(self, "Input Folder Missing", "Please select an Input Folder!")
            return

        if not output_dir:
            output_dir = DEFAULT_FOLDER
            self.output_folder_edit.setText(output_dir)

        if not output_file:
            output_file = "collage.png"
            self.output_file_edit.setText(output_file)

        full_output_path = os.path.join(output_dir, output_file)

        try:
            bgcolor_rgb = parse_color(self.bgcolor_edit.text())
            create_collage(
                input_dir=input_dir,
                width=int(self.width_edit.text()),
                height=int(self.height_edit.text()),
                bgcolor=bgcolor_rgb,
                output=full_output_path,
                max_rotation=float(self.max_rotation_edit.text()),
                overlap_factor=float(self.overlap_edit.text()),
                rows=int(self.rows_edit.text()),
                iterations=int(self.iterations_edit.text())
            )
            QMessageBox.information(self, "Success", f"Collage Created!\nFile saved to: {full_output_path}")
        except Exception as e:
            QMessageBox.critical(self, "Error Creating Collage", str(e))


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = CollageApp()
    # window.resize(700, 580)
    window.setFixedSize(700, 580)
    window.show()
    sys.exit(app.exec())
