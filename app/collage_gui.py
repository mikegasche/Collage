# ------------------------------------------------------------------------------
# Copyright (c) 2025 Michael Gasche
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.
# ------------------------------------------------------------------------------

# File:        collage_gui.py
# Version:     1.1
# Author:      Michael Gasche
# Created:     2025-12
# Product:     Collage
# Description: Graphical user interface for generating image collages.


import json
import os
import sys
from datetime import datetime

from PySide6.QtGui import QAction, QFont, QPixmap,QIcon
from PySide6.QtWidgets import (
    QApplication,
    QMainWindow,
    QWidget,
    QLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QFileDialog,
    QMessageBox,
    QVBoxLayout,
    QHBoxLayout,
    QMenuBar,
    QMenu,  
    QSizePolicy,
    QSpacerItem
)
from PySide6.QtCore import Qt

from collage import create_collage, parse_color


# --------------------------------------------------------------
# App constants
# --------------------------------------------------------------

APP_NAME = "Collage"
APP_VERSION = "1.1"
FULL_TITLE = f"{APP_NAME} {APP_VERSION}"

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

# Default input/output folder: ~/Documents
DEFAULT_FOLDER = os.path.join(os.path.expanduser("~"), "Documents")


# --------------------------------------------------------------
# Platform-specific config.json location
# --------------------------------------------------------------

def get_app_config_path():
    home = os.path.expanduser("~")
    if sys.platform == "darwin":
        base = os.path.join(home, "Library", "Application Support", "Collage")
    elif os.name == "nt":
        base = os.path.join(os.environ.get("APPDATA", home), "Collage")
    else:
        base = os.path.join(home, ".Collage")

    os.makedirs(base, exist_ok=True)
    return os.path.join(base, "config.json")


APP_CONFIG_FILE = get_app_config_path()


# --------------------------------------------------------------
# Main App Class
# --------------------------------------------------------------

class CollageApp(QMainWindow):
    def __init__(self):
        super().__init__()

        self.recent_configs = []
        self.current_config_path = None

        self.setWindowTitle(FULL_TITLE)
        self.setFixedSize(700, 608)

        # zentraler Widget-Container
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)

        # nur ein Layout für alles
        self.main_layout = QVBoxLayout()
        self.main_layout.setContentsMargins(15, 10, 15, 10)
        self.main_layout.setSpacing(10)
        self.central_widget.setLayout(self.main_layout)

        # Setup UI und Menü
        self.setup_ui()
        self.setup_menu()

        self.load_app_config()
        self.try_load_last_used_config()
        self.update_window_title()

    # ----------------------------------------------------------
    # UI Construction
    # ----------------------------------------------------------

    def setup_ui(self):
        layout = self.main_layout
        layout.setContentsMargins(15, 10, 15, 10)
        layout.setSpacing(10)

        layout.addSpacerItem(QSpacerItem(10, 20, QSizePolicy.Minimum, QSizePolicy.Fixed))

        # ------------------ TITLE IMAGE + TEXT ------------------------------
        hbox_title = QHBoxLayout()

        # Spacer left
        hbox_title.addStretch(100)

        # Image
        title_img_path = self.resource_path("title.png")
        if os.path.exists(title_img_path):
            pixmap = QPixmap(title_img_path)
            title_icon = QLabel()
            title_icon.setPixmap(pixmap)
            title_icon.setAlignment(Qt.AlignVCenter | Qt.AlignLeft)
            hbox_title.addWidget(title_icon)

        hbox_title.addStretch()

        # Text
        title = QLabel(APP_NAME)
        if sys.platform == "win32":
            font_size = 64
        else:
            font_size = 78
        title.setFont(QFont("Arial", font_size, QFont.Bold))
        title.setStyleSheet("color: #abd0da;") # #62c6ff 
        title.setAlignment(Qt.AlignVCenter | Qt.AlignLeft)
        hbox_title.addWidget(title)

        # optional Spacer left, if text is not too close to the image
        hbox_title.addStretch(100)

        # Spacer right
        layout.addLayout(hbox_title)

        layout.addSpacerItem(QSpacerItem(10, 20, QSizePolicy.Minimum, QSizePolicy.Fixed))

        self.input_folder_edit = self.add_labeled_folder(layout, "Input Folder", DEFAULT_FOLDER)
        self.output_folder_edit = self.add_labeled_folder(layout, "Output Folder", DEFAULT_FOLDER)
        self.output_file_edit = self.add_labeled_input(layout, "Output File", DEFAULTS["output_file"])
        self.width_edit = self.add_labeled_input(layout, "Collage Width", str(DEFAULTS["width"]))
        self.height_edit = self.add_labeled_input(layout, "Collage Height", str(DEFAULTS["height"]))
        self.bgcolor_edit = self.add_labeled_input(layout, "Background Color", DEFAULTS["bgcolor"])
        self.max_rotation_edit = self.add_labeled_input(layout, "Max Rotation", str(DEFAULTS["max_rotation"]))
        self.overlap_edit = self.add_labeled_input(layout, "Overlap Factor", str(DEFAULTS["overlap_factor"]))
        self.rows_edit = self.add_labeled_input(layout, "Rows (0=auto)", str(DEFAULTS["rows"]))
        self.iterations_edit = self.add_labeled_input(layout, "Iterations", str(DEFAULTS["iterations"]))

        layout.addSpacerItem(QSpacerItem(0, 10, QSizePolicy.Minimum, QSizePolicy.Fixed))

        btn_container = QWidget()
        btn_container.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Minimum)
        btn_container.setFixedWidth(176)
        btn_container.setFixedHeight(32)

        btns = QHBoxLayout(btn_container)
        btns.setContentsMargins(0, 0, 0, 0)
        btns.setSpacing(10)
        btns.setSizeConstraint(QLayout.SetFixedSize)

        run_btn = QPushButton("Run")
        run_btn.setFixedSize(80, 32)
        run_btn.clicked.connect(self.run_collage)
        exit_btn = QPushButton("Exit")
        exit_btn.setFixedSize(80, 32)
        exit_btn.clicked.connect(self.close)

        run_btn.setStyleSheet("""
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

        exit_btn.setStyleSheet("""
            QPushButton {
                padding: 8px 16px;
                border-radius: 6px;
                background-color: #747474;
                color: white;
            }
            QPushButton:hover {
                background-color: #909090;
            }
        """)

        btns.addWidget(run_btn)
        btns.addWidget(exit_btn)
        layout.addWidget(btn_container, alignment=Qt.AlignCenter)

        layout.addSpacerItem(QSpacerItem(0, 6, QSizePolicy.Minimum, QSizePolicy.Fixed))

    # ----------------------------------------------------------
    # Menu
    # ----------------------------------------------------------

    def setup_menu(self):
        menubar = self.menuBar()  # QMainWindow own menubar

        # File Menu
        file_menu = menubar.addMenu("&File")
        file_menu.addAction(self.create_action("New…", self.new_config))
        file_menu.addAction(self.create_action("Load Config…", self.load_config_dialog))
        file_menu.addAction(self.create_action("Save Config As…", self.save_config_dialog))
        
        recent_menu = QMenu("Recent Configurations", self)
        self.recent_menu = recent_menu
        self.rebuild_recent_menu()
        file_menu.addSeparator()
        file_menu.addMenu(recent_menu)

        # Help Menu
        help_menu = menubar.addMenu("&Help")
        help_menu.addAction(self.create_action("About", self.show_about))

    def create_action(self, name, func):
        action = QAction(name, self)
        action.triggered.connect(func)
        return action

    # ----------------------------------------------------------
    # Resource & MessageBox Helpers
    # ----------------------------------------------------------

    def resource_path(self, filename: str) -> str:
        if getattr(sys, "frozen", False):
            # Pfad im gebündelten PyInstaller Build
            if sys.platform == "darwin":
                # macOS App-Bundle: Resources liegen in Contents/Resources
                base_path = os.path.join(sys._MEIPASS, "..", "Resources", "resources")
            else:
                # Windows oder Linux: direkt im temporären Ordner
                base_path = os.path.join(sys._MEIPASS, "resources")
            base_path = os.path.abspath(base_path)
        else:
            # Entwicklung: relative Pfade
            base_path = os.path.join(os.path.dirname(__file__), "resources")
        return os.path.join(base_path, filename)


    def show_about(self):
        box = QMessageBox(self)
        box.setWindowTitle("About")
        
        # App Icon
        icon_path = self.resource_path("app_icon.icns")  # oder .png, je nach Build
        if os.path.exists(icon_path):
            box.setIconPixmap(QPixmap(icon_path).scaled(64, 64, Qt.KeepAspectRatio, Qt.SmoothTransformation))
        else:
            box.setIcon(QMessageBox.Information)
        
        # Text
        box.setText(f"{APP_NAME}\nVersion: {APP_VERSION}\n\n© 2025 Michael Gasche\nAll rights reserved.")
        
        # Optional: OK Button
        box.setStandardButtons(QMessageBox.Ok)
        
        box.exec()

    def show_info(self, title: str, message: str):
        box = QMessageBox()
        box.setWindowTitle(title)
        box.setText(message)
        box.setIconPixmap(QPixmap(self.resource_path("information.png")))
        box.exec()

    def show_warning(self, title: str, message: str):
        box = QMessageBox()
        box.setWindowTitle(title)
        box.setText(message)
        box.setIconPixmap(QPixmap(self.resource_path("warning.png")))
        box.exec()

    def show_error(self, title: str, message: str):
        box = QMessageBox()
        box.setWindowTitle(title)
        box.setText(message)
        box.setIconPixmap(QPixmap(self.resource_path("error.png")))
        box.exec()

    # ----------------------------------------------------------
    # Labeled Inputs & Folder
    # ----------------------------------------------------------

    def add_labeled_input(self, parent_layout, label_text, default_value):
        hbox = QHBoxLayout()
        label = QLabel(label_text)
        label.setFixedWidth(140)
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
        label.setFixedWidth(140)
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

        btn = QPushButton("Browse")
        btn.setStyleSheet("""
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
        btn.clicked.connect(lambda _, e=edit: self.browse_folder(e))
        hbox.addWidget(btn)

        parent_layout.addLayout(hbox)
        return edit

    def browse_folder(self, edit_widget):
        folder = QFileDialog.getExistingDirectory(self, "Select Folder", edit_widget.text())
        if folder:
            edit_widget.setText(folder)

    # ----------------------------------------------------------
    # Run Collage
    # ----------------------------------------------------------

    def run_collage(self):
        input_dir = self.input_folder_edit.text().strip()
        output_dir = self.output_folder_edit.text().strip()
        output_file = self.output_file_edit.text().strip() or "collage.png"

        if not input_dir:
            self.show_warning("Missing Input Folder", "Please select an Input Folder.")
            return

        if not output_dir:
            output_dir = DEFAULT_FOLDER

        full_output_path = os.path.join(output_dir, output_file)

        try:
            bgcolor_rgb = parse_color(self.bgcolor_edit.text())
            result = create_collage(
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

            if not result:  # If create_collage None or empty list returns
                self.show_warning("No Images Found",
                                f"No image files were found in the folder:\n{input_dir}")
                return
        
            self.show_info("Success", f"Collage Created!\nSaved to:\n{full_output_path}")

        except Exception as e:
            self.show_error("Error", str(e))

    # ----------------------------------------------------------
    # CONFIG PARAM SAVE / LOAD (user files)
    # ----------------------------------------------------------

    def collect_params(self):
        return {
            "input_folder": self.input_folder_edit.text(),
            "output_folder": self.output_folder_edit.text(),
            "output_file": self.output_file_edit.text(),
            "width": int(self.width_edit.text()),
            "height": int(self.height_edit.text()),
            "bgcolor": self.bgcolor_edit.text(),
            "max_rotation": float(self.max_rotation_edit.text()),
            "overlap_factor": float(self.overlap_edit.text()),
            "rows": int(self.rows_edit.text()),
            "iterations": int(self.iterations_edit.text())
        }

    def apply_params(self, params):
        self.input_folder_edit.setText(params.get("input_folder", DEFAULT_FOLDER))
        self.output_folder_edit.setText(params.get("output_folder", DEFAULT_FOLDER))
        self.output_file_edit.setText(params.get("output_file", DEFAULTS["output_file"]))
        self.width_edit.setText(str(params.get("width", DEFAULTS["width"])))
        self.height_edit.setText(str(params.get("height", DEFAULTS["height"])))
        self.bgcolor_edit.setText(params.get("bgcolor", DEFAULTS["bgcolor"]))
        self.max_rotation_edit.setText(str(params.get("max_rotation", DEFAULTS["max_rotation"])))
        self.overlap_edit.setText(str(params.get("overlap_factor", DEFAULTS["overlap_factor"])))
        self.rows_edit.setText(str(params.get("rows", DEFAULTS["rows"])))
        self.iterations_edit.setText(str(params.get("iterations", DEFAULTS["iterations"])))

    # ----------------------------------------------------------
    # New Config
    # ----------------------------------------------------------

    def new_config(self):
        """Resets all fields to default values and clears current config."""
        self.current_config_path = None
        self.apply_params({
            "input_folder": DEFAULT_FOLDER,
            "output_folder": DEFAULT_FOLDER,
            "output_file": DEFAULTS["output_file"],
            "width": DEFAULTS["width"],
            "height": DEFAULTS["height"],
            "bgcolor": DEFAULTS["bgcolor"],
            "max_rotation": DEFAULTS["max_rotation"],
            "overlap_factor": DEFAULTS["overlap_factor"],
            "rows": DEFAULTS["rows"],
            "iterations": DEFAULTS["iterations"]
        })
        self.update_window_title()

    # ----------------------------------------------------------
    # SAVE / LOAD CONFIG FILES (user-level .json)
    # ----------------------------------------------------------

    def save_config_dialog(self):
        path, _ = QFileDialog.getSaveFileName(self, "Save Config", DEFAULT_FOLDER, "JSON (*.json)")
        if not path:
            return

        data = self.collect_params()

        try:
            with open(path, "w") as f:
                json.dump(data, f, indent=4)

            self.add_recent_config(path)
            self.current_config_path = path
            self.update_window_title()
            self.show_info("Saved", "Configuration saved.")

        except Exception as e:
            self.show_error("Error", f"Could not save file:\n{e}")

    def load_config_dialog(self):
        path, _ = QFileDialog.getOpenFileName(self, "Load Config", DEFAULT_FOLDER, "JSON (*.json)")
        if not path:
            return
        self.load_config(path)

    def load_config(self, path):
        if not os.path.exists(path):
            self.show_warning("Missing File", "This config file no longer exists.")
            self.remove_recent_config(path)
            return

        try:
            with open(path, "r") as f:
                params = json.load(f)

            self.apply_params(params)
            self.add_recent_config(path)
            self.current_config_path = path
            self.update_window_title()

        except Exception as e:
            self.show_error("Error", f"Could not load config:\n{e}")

    # ----------------------------------------------------------
    # RECENT CONFIGS
    # ----------------------------------------------------------

    def add_recent_config(self, path):
        path = os.path.abspath(path)

        # Remove duplicates
        self.recent_configs = [p for p in self.recent_configs if p["path"] != path]

        self.recent_configs.insert(0, {"path": path, "timestamp": datetime.now().isoformat()})

        self.recent_configs = self.recent_configs[:10]  # Keep max 10
        self.save_app_config()
        self.rebuild_recent_menu()

    def remove_recent_config(self, path):
        path = os.path.abspath(path)
        self.recent_configs = [p for p in self.recent_configs if p["path"] != path]
        self.save_app_config()
        self.rebuild_recent_menu()

    def rebuild_recent_menu(self):
        # make sure recent_menu exists
        try:
            self.recent_menu.clear()
        except Exception:
            return

        if not self.recent_configs:
            empty = QAction("(none)", self)
            empty.setEnabled(False)
            self.recent_menu.addAction(empty)
            return

        for entry in self.recent_configs:
            # show base filename and attach full path
            label = os.path.basename(entry["path"])
            action = QAction(label, self)
            action.triggered.connect(lambda _, p=entry["path"]: self.load_config(p))
            self.recent_menu.addAction(action)

    # ----------------------------------------------------------
    # APP CONFIG (only meta info)
    # ----------------------------------------------------------

    def load_app_config(self):
        if not os.path.exists(APP_CONFIG_FILE):
            return

        try:
            with open(APP_CONFIG_FILE, "r") as f:
                data = json.load(f)

            # expect recent_configs as list of {"path":..., "timestamp":...}
            self.recent_configs = data.get("recent_configs", [])
            self.current_config_path = data.get("last_loaded_config")

        except Exception:
            # ignore parse errors, start fresh
            self.recent_configs = []
            self.current_config_path = None

        # Auto-clean removed files
        cleaned = []
        for entry in self.recent_configs:
            if os.path.exists(entry.get("path", "")):
                cleaned.append(entry)
        self.recent_configs = cleaned

        # persist cleaned state
        self.save_app_config()
        self.rebuild_recent_menu()

    def save_app_config(self):
        data = {
            "last_loaded_config": self.current_config_path,
            "recent_configs": self.recent_configs
        }
        try:
            with open(APP_CONFIG_FILE, "w") as f:
                json.dump(data, f, indent=4)
        except Exception as e:
            self.show_error("Error", f"Could not save app config:\n{e}")

    def try_load_last_used_config(self):
        if self.current_config_path and os.path.exists(self.current_config_path):
            self.load_config(self.current_config_path)
        else:
            # clear if missing
            self.current_config_path = None
            self.update_window_title()

    # ----------------------------------------------------------
    # TITLE MANAGEMENT
    # ----------------------------------------------------------

    def update_window_title(self):
        if self.current_config_path and os.path.exists(self.current_config_path):
            name = os.path.basename(self.current_config_path)
            self.setWindowTitle(f"{FULL_TITLE} - {name}")
        else:
            self.setWindowTitle(FULL_TITLE)


# --------------------------------------------------------------
# MAIN
# --------------------------------------------------------------

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = CollageApp()
    if sys.platform == "win32":
        icon_file = "app_icon.ico"
    elif sys.platform == "darwin":
        icon_file = "app_icon.icns"
    else:
        icon_file = "app_icon.png"
    window.setWindowIcon(QIcon(window.resource_path(icon_file)))
    window.show()
    sys.exit(app.exec())
