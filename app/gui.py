import os.path

from PyQt6.QtWidgets import (QApplication, QGridLayout, QVBoxLayout, QFormLayout, QWidget, QPushButton, QLabel,
                             QLineEdit,
                             QCheckBox, QSpinBox, QComboBox, QSpacerItem, QSizePolicy, QGroupBox, QHBoxLayout,
                             QFileDialog, QListWidget, QRadioButton)
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

            # Make "Directory" box =====================================================================================
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
            self.center_layout = QGridLayout()
            self.group_box_02_a = QGroupBox("Folders")
            self.group_box_02_b = QGroupBox("Files")
            self.group_box_02_c = QGroupBox("Settings")
            self.group_box_layout_02 = QHBoxLayout()
            self.group_box_layout_02_a = QVBoxLayout()
            self.group_box_layout_02_b = QVBoxLayout()
            self.group_box_layout_02_c = QHBoxLayout()

            # Create a QListWidget
            self.list_widget_a = QListWidget()
            self.list_widget_a.currentItemChanged.connect(self.update_widget_b_items)
            self.list_widget_b = QListWidget()

            # Layout grid items
            self.center_layout.addWidget(self.group_box_02_a, 0, 0, 10, 1)
            self.center_layout.addWidget(self.group_box_02_c, 0, 1, 1, 1)
            self.center_layout.addWidget(self.group_box_02_b, 1, 1, 9, 1)

            # Set layouts of group items
            self.group_box_02_a.setLayout(self.group_box_layout_02_a)
            self.group_box_02_c.setLayout(self.group_box_layout_02_c)
            self.group_box_02_b.setLayout(self.group_box_layout_02_b)

            # Add lists to group items
            self.group_box_layout_02_a.addWidget(self.list_widget_a)
            self.group_box_layout_02_b.addWidget(self.list_widget_b)

            # Checkboxes
            self.check_resolution = QCheckBox("Resolution")
            self.check_HDR = QCheckBox("Dynamic Range")
            self.check_bitrate = QCheckBox("Bitrate")
            self.group_box_layout_02_c.addWidget(self.check_resolution)
            self.group_box_layout_02_c.addWidget(self.check_HDR)
            self.group_box_layout_02_c.addWidget(self.check_bitrate)

            # Make "Actions" box =======================================================================================
            self.group_box_04 = QGroupBox("Actions")
            self.group_box_layout_04 = QHBoxLayout()

            # Create a button to scan the input directory and generate the form
            self.generate_button = QPushButton("Scan Directory")
            self.generate_button.clicked.connect(self.generate_file_list)
            self.group_box_layout_04.addWidget(self.generate_button)

            # Create a button to rename all the scanned files
            self.generate_button = QPushButton("Rename")
            self.generate_button.clicked.connect(self.rename_files)
            self.group_box_layout_04.addWidget(self.generate_button)

            # Set the group box layouts ================================================================================
            self.group_box_01.setLayout(self.group_box_layout_01)
            self.group_box_04.setLayout(self.group_box_layout_04)

            # Add the group box to the main layout =====================================================================
            self.layout.addWidget(self.group_box_01)

            self.layout.addLayout(self.center_layout, stretch=1)

            self.layout.addWidget(self.group_box_04)

            # Set the layout for the window ============================================================================
            self.setLayout(self.layout)

            # Apply custom styles
            self.modern_stylesheet()
        except:
            log(4, f"CRITICAL GUI ERROR")

    def generate_file_list(self):

        try:
            log(1, f"Generating file list...")

            # Clear any existing items from our lists
            self.list_widget_a.clear()
            self.list_widget_b.clear()

            # Get all the movie folders in our input directory
            movie_folders = SB_EXECUTE.get_movie_folders(self.directory_path)

            # Create a dictionary with parsed movie names and their original path
            self.parsed_movie_folder_dict = {}
            for movie in movie_folders:
                name = SB_FILES.parse_movie_name(movie)
                self.parsed_movie_folder_dict[name] = movie

            # Parse all the video names in each movie folder and add them to a dictionary
            # {'parsed_movie_name' : {'parsed_video_name' : 'video_path'}}
            self.parsed_video_dict = {}
            for movie in self.parsed_movie_folder_dict:
                # Create the dictionary for all video files
                self.parsed_video_dict[movie] = {}

                # Get all video files in the current directory
                video_files = SB_FILES.get_files_in_directory(self.parsed_movie_folder_dict[movie])

                # Get rid of any files that don't have a video extension
                only_videos = []
                for video in video_files:
                    if video.endswith(".mkv") or video.endswith(".mp4"):
                        only_videos.append(video)
                        log(0, f"Video       : {video}")
                    else:
                        log(0, f"Not a video : {video}")

                # Parse all the video names
                log(0, f"Resolution    : {self.check_resolution.isChecked()}")
                log(0, f"Bitrate       : {self.check_bitrate.isChecked()}")
                log(0, f"Dynamic Range : {self.check_HDR.isChecked()}")
                for video in only_videos:
                    parsed_video_name = SB_FILES.parse_video_name(video_path=video, parsed_movie_name=movie,
                                                                  get_resolution=self.check_resolution.isChecked(),
                                                                  get_bitrate=self.check_bitrate.isChecked(),
                                                                  get_dynamic_range=self.check_HDR.isChecked())
                    self.parsed_video_dict[movie][parsed_video_name] = video

            # Add the updated names to the UI ==========================================================================
            # Figure out which widget_a item is selected, and display those items
            self.list_widget_a.addItems(self.parsed_movie_folder_dict.keys())

            # This automatically updates widget_list_b so we don't need to call an update manually
            self.list_widget_a.setCurrentRow(0)

        except:
            log(4, f"CRITICAL ERROR")

    def update_widget_b_items(self):
        log(1, f"Active movie changed. Updating lists...")

        # Clear any existing items from our lists
        self.list_widget_b.clear()

        log(0, f"Active movie : {self.list_widget_a.currentItem().text()}")
        log(0, f"Dict : {self.parsed_video_dict}")

        self.list_widget_b.addItems(self.parsed_video_dict[self.list_widget_a.currentItem().text()].keys())
        self.list_widget_b.setCurrentRow(0)

    def rename_files(self):
        log(1, f"RENAME FILES")

    def select_directory(self):
        # Open file dialog
        self.directory_path = QFileDialog.getExistingDirectory(self, "Select Directory", "")
        if self.directory_path:
            # Update the label with the selected file path
            self.directory_label.setText(f"{self.directory_path}")

    def modern_stylesheet(app: QApplication):
        """
        Apply a dark blue theme to the given QApplication.
        """
        app.setStyleSheet("""
            /* General Application Styles */
            QWidget {
                background-color: #1c1f26;  /* Dark blue background */
                color: #ffffff;            /* White text */
                font-family: 'Segoe UI', 'Arial', sans-serif;  /* Clean font */
                font-size: 14px;           /* Slightly larger text */
            }

            /* Buttons */
            QPushButton {
                background-color: #283144; /* Darker blue for buttons */
                color: #ffffff;
                border: 1px solid #3e4b61;
                border-radius: 5px;
                padding: 6px 12px;
            }
            QPushButton:hover {
                background-color: #3e4b61; /* Lighter blue on hover */
            }
            QPushButton:pressed {
                background-color: #53637d; /* Even lighter blue when pressed */
            }

            /* Labels */
            QLabel {
                font-size: 16px;          /* Larger text for labels */
            }

            /* Checkboxes and Radio Buttons */
            QCheckBox, QRadioButton {
                spacing: 8px;             /* Add spacing between label and box */
            }
            QCheckBox::indicator, QRadioButton::indicator {
                width: 16px;
                height: 16px;
            }
            QCheckBox::indicator {
                border: 1px solid #3e4b61;
                background-color: #283144;
            }
            QCheckBox::indicator:checked {
                background-color: #0078d4; /* Bright blue check */
                border: 1px solid #0078d4;
            }
            QRadioButton::indicator {
                border: 1px solid #3e4b61;
                background-color: #283144;
            }
            QRadioButton::indicator:checked {
                background-color: #0078d4;
                border: 1px solid #0078d4;
            }

            /* LineEdit */
            QLineEdit {
                background-color: #2a2f38;
                color: #ffffff;
                border: 1px solid #3e4b61;
                border-radius: 4px;
                padding: 4px;
            }

            /* List Widgets */
            QListWidget {
                background-color: #2a2f38;
                color: #ffffff;
                border: 1px solid #3e4b61;
                padding: 4px;
            }
            QListWidget::item {
                padding: 8px;
            }
            QListWidget::item:selected {
                background-color: #3e4b61;
                color: #ffffff;
            }

            /* Progress Bars */
            QProgressBar {
                text-align: center;
                color: #ffffff;
                background-color: #2a2f38;
                border: 1px solid #3e4b61;
                border-radius: 4px;
            }
            QProgressBar::chunk {
                background-color: #0078d4; /* Bright blue progress */
            }

            /* Scrollbars */
            QScrollBar:vertical, QScrollBar:horizontal {
                background-color: #2a2f38;
                border: none;
                width: 10px;
                margin: 0px;
            }
            QScrollBar::handle {
                background-color: #3e4b61;
                border-radius: 5px;
            }
            QScrollBar::handle:hover {
                background-color: #53637d;
            }
        """)