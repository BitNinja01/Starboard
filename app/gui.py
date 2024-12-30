import os.path

from PyQt6.QtWidgets import (QApplication, QVBoxLayout, QFormLayout, QWidget, QPushButton, QLabel, QLineEdit,
                             QCheckBox, QSpinBox, QComboBox, QSpacerItem, QSizePolicy, QGroupBox, QHBoxLayout)
from PyQt6.QtGui import QIcon
from utilities import SB_EXECUTE, SB_FILES
import zazzle

log = zazzle.ZZ_Logging.log

class SB_Main_Window(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Starboard")

        # Set the window icon
        self.setWindowIcon(QIcon("img/anchor.svg"))

        # Get the screen's available geometry
        screen = QApplication.primaryScreen()
        screen_geometry = screen.availableGeometry()

        # Calculate window size (e.g., 50% of screen width and 70% of screen height)
        width = int(screen_geometry.width() * 0.5)
        height = int(screen_geometry.height() * 0.7)

        # Set the window size
        self.resize(width, height)

        # Create the layout for the main window
        self.layout = QVBoxLayout()

        # Make "Directory" box =========================================================================================
        self.group_box_01 = QGroupBox("Directory")
        self.group_box_layout_01 = QHBoxLayout()

        # Create the entry line for the directory path
        self.directory_entry = QLineEdit()
        self.directory_entry.setPlaceholderText("Enter directory to scan...")
        self.group_box_layout_01.addWidget(self.directory_entry)

        # Make "Renaming" box ==========================================================================================
        self.group_box_02 = QGroupBox("Renaming")
        self.group_box_02_a = QGroupBox("Folder")
        self.group_box_02_b = QGroupBox("Files")
        self.group_box_layout_02 = QVBoxLayout()

        # Create a QFormLayout that will be dynamically populated
        self.form_layout_a = QFormLayout()
        self.form_layout_b = QFormLayout()

        # Add the form layout to the main layout
        self.group_box_layout_02.addWidget(self.group_box_02_a)
        self.group_box_layout_02.addWidget(self.group_box_02_b, stretch=1)

        self.group_box_02_a.setLayout(self.form_layout_a)
        self.group_box_02_b.setLayout(self.form_layout_b)


        # Make "Actions" box ===========================================================================================
        self.group_box_03 = QGroupBox("Actions")
        self.group_box_layout_03 = QHBoxLayout()

        # Create a button to scan the input directory and generate the form
        self.generate_button = QPushButton("Scan Directory")
        self.generate_button.clicked.connect(self.generate_file_list)
        self.group_box_layout_03.addWidget(self.generate_button)

        # Create a button to rename all the scanned files
        self.generate_button = QPushButton("Rename")
        self.generate_button.clicked.connect(self.rename_files)
        self.group_box_layout_03.addWidget(self.generate_button)

        # Set the group box layouts ====================================================================================
        self.group_box_01.setLayout(self.group_box_layout_01)
        self.group_box_02.setLayout(self.group_box_layout_02)
        self.group_box_03.setLayout(self.group_box_layout_03)

        # Add the group box to the main layout =========================================================================
        self.layout.addWidget(self.group_box_01)

        self.layout.addWidget(self.group_box_02, stretch=1)

        self.layout.addWidget(self.group_box_03)

        # Set the layout for the window ================================================================================
        self.setLayout(self.layout)

        # Apply custom styles
        self.apply_dark_theme()

    def generate_file_list(self):

        try:
            log(1, f"Generating file list...")
            log(0, f"Directory : {self.directory_entry.text()}")

            # Clear any existing fields from the form
            self.clear_form()

            movie_folders = SB_EXECUTE.get_movie_folders(self.directory_entry.text())

            # Populate the UI with all the movie folders we found
            if movie_folders:
                log(0, f"{len(movie_folders)} movie folder found!")
                for movie in movie_folders:
                    video_files = SB_FILES.get_files_in_directory(os.path.join(self.directory_entry.text(), movie))

                    for video in video_files:
                        log(0, f"Video file : {video}")

                        # Get the names for the movie file
                        base_name, detailed_name, final_name = SB_FILES.fix_base_movie_name(video)

                        log(1, f"{movie}")
                        name_label = QLabel(f"{movie}")
                        name_input = QLineEdit()
                        name_input.setText(f"{movie}")
                        self.form_layout.addRow(name_label, name_input)
        except:
            log(4, f"CRITICAL ERROR")

    def rename_files(self):
        log(1, f"RENAME FILES")

    def clear_form(self):
        # Clear the current layout (remove all widgets)
        for i in reversed(range(self.form_layout.count())):
            item = self.form_layout.itemAt(i)
            if item.widget():
                item.widget().deleteLater()

    def apply_dark_theme(self):
        # Apply a stylesheet for the dark theme
        self.setStyleSheet("""
            QWidget {
                background-color: #161c2d;
                color: #ffffff;
                font-family: Arial;
                font-size: 14px;
            }
            QLabel {
                color: #e0e0e0;
                font-weight: bold;
                padding: 5px;
            }
            QLineEdit, QComboBox, QSpinBox {
                border: 1px solid #325180;
                border-radius: 4px;
                padding: 5px;
                background-color: #1e1e1e;
                color: #ffffff;
            }
            QLineEdit:hover, QComboBox:hover, QSpinBox:hover {
                border: 1px solid #1e304d;
            }
            QLineEdit:focus, QComboBox:focus, QSpinBox:focus {
                border: 1px solid #1e304d;
            }
            QPushButton {
                background-color: #325180;
                color: white;
                border: none;
                border-radius: 4px;
                padding: 10px;
                font-size: 14px;
            }
            QPushButton:hover {
                background-color: #4f81cc;
            }
            QPushButton:pressed {
                background-color: #1e304d;
            }
            QCheckBox {
                padding: 5px;
                color: #e0e0e0;
            }
            QCheckBox::indicator {
                width: 15px;
                height: 15px;
                background-color: #161c2d;
                border: 1px solid #777;
                border-radius: 2px;
            }
            QCheckBox::indicator:checked {
                background-color: #4f81cc;
                border: 1px solid #325180;
            }
        """)