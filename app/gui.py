import os.path
from PyQt6.QtWidgets import (QApplication, QGridLayout, QVBoxLayout, QFormLayout, QWidget, QPushButton, QLabel,
                             QLineEdit,
                             QCheckBox, QSpinBox, QComboBox, QSpacerItem, QSizePolicy, QGroupBox, QHBoxLayout,
                             QFileDialog, QListWidget, QRadioButton, QProgressBar, QDialog)
from PyQt6.QtGui import QIcon
from PyQt6.QtCore import QThread, pyqtSignal, Qt
from utilities import SB_EXECUTE, SB_FILES
import zazzle
import time

log = zazzle.ZZ_Logging.log

class FileListWorker(QThread):
    progress_updated = pyqtSignal(int)
    task_finished = pyqtSignal()

    def __init__(self, gui_instance):
        super().__init__()
        self.gui_instance = gui_instance

    def run(self):
        self.gui_instance.generate_file_list(progress_callback=self.update_progress)
        self.task_finished.emit()

    def update_progress(self, value):
        self.progress_updated.emit(value)

class PopupDialog(QDialog):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Generating File List")
        self.resize(300, 100)
        self.setModal(True)

        # Set the window icon
        self.setWindowIcon(QIcon("img/anchor.svg"))

        # Layout and widgets
        layout = QVBoxLayout()
        self.label = QLabel("Processing...")
        self.progress_bar = QProgressBar()
        self.progress_bar.setValue(0)

        layout.addWidget(self.label)
        layout.addWidget(self.progress_bar)
        self.setLayout(layout)

    def update_progress(self, value):
        # Update progress bar
        self.progress_bar.setValue(value)

    def task_finished(self):
        # Update label when task is complete
        self.label.setText("Task Complete!")
        self.thread.quit()
        self.thread.wait()

        # Close the popup
        self.close()

    def center_on_screen(self):
        # Get the screen geometry
        screen_geometry = QApplication.primaryScreen().geometry()
        screen_width = screen_geometry.width()
        screen_height = screen_geometry.height()

        # Calculate the center point
        popup_width = self.width()
        popup_height = self.height()
        x = (screen_width - popup_width) // 2
        y = (screen_height - popup_height) // 2

        # Move the popup to the center
        self.move(x, y)

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

            # Create a button to scan the input directory and generate the form
            self.generate_button = QPushButton("Refresh")
            self.generate_button.clicked.connect(self.open_popup)

            # Add widgets to layout
            self.group_box_layout_01.addWidget(self.directory_label, stretch=1)
            self.group_box_layout_01.addWidget(self.generate_button)
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
            self.check_imdb_id = QCheckBox("IMDB ID")
            self.group_box_layout_02_c.addWidget(self.check_resolution)
            self.group_box_layout_02_c.addWidget(self.check_HDR)
            self.group_box_layout_02_c.addWidget(self.check_video_bitrate)
            self.group_box_layout_02_c.addWidget(self.check_audio_codec)
            self.group_box_layout_02_c.addWidget(self.check_video_framerate)
            self.group_box_layout_02_c.addWidget(self.check_video_colorspace)
            self.group_box_layout_02_c.addWidget(self.check_imdb_id)

            # Make "Actions" box =======================================================================================
            self.group_box_04 = QGroupBox("Actions")
            self.group_box_layout_04 = QHBoxLayout()

            # Create a button to rename all the scanned files
            self.rename = QPushButton("Rename")
            self.rename.clicked.connect(self.rename_files)

            self.rename_all_button = QPushButton("Rename All")
            self.rename_all_button.clicked.connect(self.rename_all_files)

            # Add the buttons to the layout
            self.group_box_layout_04.addWidget(self.rename)
            self.group_box_layout_04.addWidget(self.rename_all_button)

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

    def open_popup(self):
        # Create the popup
        self.progress_popup = PopupDialog()

        # Create the worker thread
        self.worker = FileListWorker(self)
        self.worker.progress_updated.connect(self.progress_popup.progress_bar.setValue)
        self.worker.task_finished.connect(self.progress_popup.close)
        self.worker.task_finished.connect(self.cleanup_popup)

        # Start the worker thread and show the popup
        self.worker.start()
        self.progress_popup.exec()

    def generate_file_list(self, progress_callback=None):
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

            # Handle progress bar updates
            total_movies = len(movie_folders)
            current_progress = 0

            self.parsed_movie_folder_dict = {
                SB_FILES.parse_movie_name(movie): movie for movie in movie_folders
            }
            self.parsed_video_dict = {
                movie: {} for movie in self.parsed_movie_folder_dict
            }

            # Get all our files in dictionaries
            for i, (movie, path) in enumerate(self.parsed_movie_folder_dict.items()):
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
                        get_video_colorspace=self.check_video_colorspace.isChecked(),
                        get_imdb_id=self.check_imdb_id.isChecked()
                    )
                    self.parsed_video_dict[movie][parsed_video_name] = video

                # Update progress
                current_progress = int(((i + 1) / total_movies) * 100)
                if progress_callback:
                    progress_callback(current_progress)

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
        log(1, f"Renaming selected files")

        # Rename all the videos
        for index in range(self.list_widget_b.count()):
            log(0, f"Waling through list items")
            list_b_item = self.list_widget_b.item(index)
            video = list_b_item.text()
            log(0, f"video : {video}")

            # Get the old and new path for the current video
            current_movie = self.list_widget_a.currentItem().text()
            old_video_path = self.parsed_video_dict[current_movie][video]
            log(0, f"old_video_path : {self.parsed_video_dict[current_movie][video]}")
            new_video_path = old_video_path.rpartition("\\")[0]
            log(0, f"new_video_path : {new_video_path}")
            new_video_path = f"{new_video_path}\\{video}"
            log(0, f"new_video_path : {new_video_path}")

            SB_FILES.rename_files(old_video_path, new_video_path)

        # Rename the movie folder
        current_movie = self.list_widget_a.currentItem().text()
        log(0, f"current_movie : {current_movie}")
        old_folder_name = self.parsed_movie_folder_dict[current_movie]
        log(0, f"old_folder_name : {old_folder_name}")
        new_folder_name = old_folder_name.rpartition("\\")[0]
        log(0, f"new_folder_name : {new_folder_name}")
        new_folder_name = f"{new_folder_name}\\{current_movie}"
        log(0, f"new_folder_name : {new_folder_name}")

        SB_FILES.rename_files(old_folder_name, new_folder_name)

        log(0, f"Clear widget_list_b")
        # Remove all items from widget_list_b
        self.list_widget_b.clear()

        # Remove the active item from widget_list_a
        current_row = self.list_widget_a.currentRow()
        if current_row != -1:
            item = self.list_widget_a.takeItem(current_row)
        else:
            print("No item selected to remove.")

        # Delete the item from memory
        del item

        # Clear selection to prevent errors
        self.list_widget_a.clearSelection()

        # Make index 1 active
        self.list_widget_a.setCurrentRow(0)

    def rename_all_files(self):
        for index in range(self.list_widget_a.count()):
            self.rename_files()

    def select_directory(self):
        try:
            # Open directory selection dialog
            self.directory_path = QFileDialog.getExistingDirectory(self, "Select Directory", "")

            # Check if a directory was selected
            if self.directory_path:
                log(1, f"Selected directory: {self.directory_path}")
                self.directory_label.setText(f"{self.directory_path}")

                # Proceed to open the progress popup
                self.open_popup()
            else:
                log(3, "No directory selected.")

        except Exception as e:
            log(4, f"Error selecting directory: {e}")

    def cleanup_popup(self):
        log(1, "Popup closed and task finished.")
        self.progress_popup = None  # Clear popup reference
        self.worker = None  # Clear worker reference

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