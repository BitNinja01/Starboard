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
            self.check_video_bitrate = QCheckBox("Video Bitrate")
            self.check_audio_codec = QCheckBox("Audio Codec")
            self.check_video_framerate = QCheckBox("Framerate")
            self.check_video_colorspace = QCheckBox("Colorspace")
            self.group_box_layout_02_c.addWidget(self.check_resolution)
            self.group_box_layout_02_c.addWidget(self.check_HDR)
            self.group_box_layout_02_c.addWidget(self.check_video_bitrate)
            self.group_box_layout_02_c.addWidget(self.check_audio_codec)
            self.group_box_layout_02_c.addWidget(self.check_video_framerate)
            self.group_box_layout_02_c.addWidget(self.check_video_colorspace)

            # Make "Actions" box =======================================================================================
            self.group_box_04 = QGroupBox("Actions")
            self.group_box_layout_04 = QHBoxLayout()

            # Create a button to scan the input directory and generate the form
            self.generate_button = QPushButton("Update Names")
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
            self.list_widget_a.clear()
            self.list_widget_b.clear()

            if not hasattr(self, 'directory_path') or not os.path.exists(self.directory_path):
                log(3, f"Invalid or missing directory path: {self.directory_path}")
                return

            movie_folders = SB_EXECUTE.get_movie_folders(self.directory_path)
            if not movie_folders:
                log(3, "No movie folders found.")
                return

            self.parsed_movie_folder_dict = {
                SB_FILES.parse_movie_name(movie): movie for movie in movie_folders
            }
            self.parsed_video_dict = {
                movie: {} for movie in self.parsed_movie_folder_dict
            }

            for movie, path in self.parsed_movie_folder_dict.items():
                video_files = SB_FILES.get_files_in_directory(path)
                video_files = [v for v in video_files if v.endswith(('.mkv', '.mp4'))]

                for video in video_files:
                    parsed_video_name = SB_FILES.parse_video_name(
                        video_path=video, parsed_movie_name=movie,
                        get_resolution=self.check_resolution.isChecked(),
                        get_video_bitrate=self.check_video_bitrate.isChecked(),
                        get_dynamic_range=self.check_HDR.isChecked(),
                        get_audio_codec=self.check_audio_codec.isChecked(),
                        get_video_framerate=self.check_video_framerate.isChecked(),
                        get_video_colorspace=self.check_video_colorspace.isChecked()
                    )
                    self.parsed_video_dict[movie][parsed_video_name] = video

            if not self.parsed_movie_folder_dict:
                log(3, "No parsed movie folders to display.")
                return

            self.list_widget_a.addItems(self.parsed_movie_folder_dict.keys())
            self.list_widget_a.setCurrentRow(0)

        except Exception as e:
            log(4, f"CRITICAL ERROR: {e}")

    def update_widget_b_items(self):
        log(1, f"Active movie changed. Updating lists...")
        self.list_widget_b.clear()

        current_item = self.list_widget_a.currentItem()
        if not current_item:
            log(3, "No active movie selected.")
            return

        movie_name = current_item.text()
        if movie_name not in self.parsed_video_dict:
            log(3, f"Movie '{movie_name}' not found in parsed_video_dict.")
            return

        log(0, f"Active movie: {movie_name}")
        self.list_widget_b.addItems(self.parsed_video_dict[movie_name].keys())
        self.list_widget_b.setCurrentRow(0)

    def rename_files(self):
        log(1, f"RENAME FILES")

    def select_directory(self):
        # Open file dialog
        self.directory_path = QFileDialog.getExistingDirectory(self, "Select Directory", "")
        if self.directory_path:
            # Update the label with the selected file path
            self.directory_label.setText(f"{self.directory_path}")
            self.generate_file_list()

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