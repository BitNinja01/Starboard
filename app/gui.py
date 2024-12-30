import os.path

from PyQt6.QtWidgets import (QApplication, QVBoxLayout, QFormLayout, QWidget, QPushButton, QLabel, QLineEdit,
                             QCheckBox, QSpinBox, QComboBox, QSpacerItem, QSizePolicy, QGroupBox, QHBoxLayout,
                             QFileDialog, QListWidget)
from PyQt6.QtGui import QIcon
from utilities import SB_EXECUTE, SB_FILES
import zazzle

log = zazzle.ZZ_Logging.log

class SB_Main_Window(QWidget):
    def __init__(self):
        try:
            super().__init__()
            self.setWindowTitle("Starboard")

            # Set the window icon
            self.setWindowIcon(QIcon("img/anchor.svg"))

            # Create the layout for the main window
            self.layout = QVBoxLayout()

            # Make "Directory" box =========================================================================================
            self.group_box_01 = QGroupBox("Directory")
            self.group_box_layout_01 = QHBoxLayout()

            # Create the entry line for the directory path
            self.select_directory_button = QPushButton("Select Folder")
            self.select_directory_button.clicked.connect(self.select_directory)
            self.directory_label = QLabel("Selected file path will appear here")

            # Add widgets to layout
            self.group_box_layout_01.addWidget(self.directory_label, stretch=1)
            self.group_box_layout_01.addWidget(self.select_directory_button)

            # Make Renaming section ====================================================================================
            self.movie_folders = []
            self.video_files = []
            self.group_box_02 = QHBoxLayout()
            self.group_box_02_a = QGroupBox("Folders")
            self.group_box_02_b = QGroupBox("Files")
            self.group_box_layout_02 = QHBoxLayout()
            self.group_box_layout_02_a = QVBoxLayout()
            self.group_box_layout_02_b = QVBoxLayout()

            # Add the form layout to the main layout
            self.group_box_layout_02.addWidget(self.group_box_02_a, stretch=1)
            self.group_box_layout_02.addWidget(self.group_box_02_b, stretch=2)

            # Set up the vertical layouts for each file list box
            self.group_box_02_a.setLayout(self.group_box_layout_02_a)
            self.group_box_02_b.setLayout(self.group_box_layout_02_b)

            # Create a QListWidget
            self.list_widget_a = QListWidget()
            self.list_widget_b = QListWidget()
            self.group_box_layout_02_a.addWidget(self.list_widget_a)
            self.group_box_layout_02_b.addWidget(self.list_widget_b)


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
            self.group_box_02.addLayout(self.group_box_layout_02)
            self.group_box_03.setLayout(self.group_box_layout_03)

            # Add the group box to the main layout =========================================================================
            self.layout.addWidget(self.group_box_01)

            self.layout.addLayout(self.group_box_02, stretch=1)

            self.layout.addWidget(self.group_box_03)

            # Set the layout for the window ================================================================================
            self.setLayout(self.layout)

            # Apply custom styles
            self.modern_stylesheet()
        except:
            log(4, f"CRITICAL GUI ERROR")

    def generate_file_list(self):

        try:
            log(1, f"Generating file list...")

            # Clear any existing items from our list
            self.list_widget_a.clear()

            # Get all the movie folders in our input directory
            movie_folders = SB_EXECUTE.get_movie_folders(self.directory_path)

            # Create a dictionary with parsed movie names and their original path
            parsed_movie_folder_dict = {}
            for movie in movie_folders:
                name = SB_FILES.parse_movie_name(movie)
                parsed_movie_folder_dict[name] = movie

            # Add the updated names to the UI
            self.list_widget_a.addItems(parsed_movie_folder_dict.keys())

            # Populate the UI with all the movie folders we found
            """if movie_folders:
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
                        self.form_layout.addRow(name_label, name_input)"""
        except:
            log(4, f"CRITICAL ERROR")

    def rename_files(self):
        log(1, f"RENAME FILES")

    def select_directory(self):
        # Open file dialog
        self.directory_path = QFileDialog.getExistingDirectory(self, "Select Directory", "")
        if self.directory_path:
            # Update the label with the selected file path
            self.directory_label.setText(f"{self.directory_path}")

    def modern_stylesheet(self):
        return """
        QWidget {
            background-color: #2c2f33;
            color: #ffffff;
            font-family: Arial, sans-serif;
            font-size: 16px;
        }

        QLabel#headerLabel {
            font-size: 24px;
            font-weight: bold;
            color: #7289da;
            margin-bottom: 24px;
        }

        QLineEdit {
            background-color: #23272a;
            border: 2px solid #99aab5;
            border-radius: 8px;
            padding: 8px;
            color: #ffffff;
            font-size: 16px;
        }
        QLineEdit:focus {
            border-color: #7289da;
        }

        QListWidget {
            background-color: #23272a;
            border: 2px solid #99aab5;
            border-radius: 8px;
            padding: 4px;
            font-size: 16px;
        }
        QListWidget::item {
            padding: 8px;
            border-radius: 4px;
        }
        QListWidget::item:selected {
            background-color: #7289da;
            color: #ffffff;
        }

        QPushButton#primaryButton {
            background-color: #7289da;
            color: #ffffff;
            font-weight: bold;
            border: none;
            border-radius: 8px;
            padding: 10px 20px;
            font-size: 16px;
        }
        QPushButton#primaryButton:hover {
            background-color: #5b6eae;
        }
        QPushButton#primaryButton:pressed {
            background-color: #4e5e96;
        }
        """