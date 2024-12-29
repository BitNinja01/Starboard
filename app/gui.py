from PyQt6.QtWidgets import (QApplication, QVBoxLayout, QFormLayout, QWidget, QPushButton, QLabel, QLineEdit,
                             QCheckBox, QSpinBox, QComboBox, QSpacerItem, QSizePolicy)


class SB_Main_Window(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Starboard")

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

        # Create the entry line for the directory path
        self.directory_entry = QLineEdit()
        self.directory_entry.setPlaceholderText("Enter directory to scan...")
        self.layout.addWidget(self.directory_entry)

        # Add a spacer item to push everything above
        spacer = QSpacerItem(20, 40, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)
        self.layout.addItem(spacer)

        # Create a QFormLayout that will be dynamically populated
        self.form_layout = QFormLayout()

        # Add the form layout to the main layout
        self.layout.addLayout(self.form_layout)

        # Create checkboxes to control which fields should appear in the form
        self.name_checkbox = QCheckBox("Include Name")
        self.age_checkbox = QCheckBox("Include Age")
        self.gender_checkbox = QCheckBox("Include Gender")

        # Add checkboxes to the layout
        self.layout.addWidget(self.name_checkbox)
        self.layout.addWidget(self.age_checkbox)
        self.layout.addWidget(self.gender_checkbox)

        # Create a button to generate the form
        self.generate_button = QPushButton("Generate Form")
        self.generate_button.clicked.connect(self.generate_form)

        # Add the button to the layout
        self.layout.addWidget(self.generate_button)

        # Set the layout for the window
        self.setLayout(self.layout)

        # Apply custom styles
        self.apply_dark_theme()

    def generate_form(self):
        # Clear any existing fields from the form
        self.clear_form()

        # Dynamically add fields based on checkbox state
        if self.name_checkbox.isChecked():
            name_label = QLabel("Name:")
            name_input = QLineEdit()
            self.form_layout.addRow(name_label, name_input)

        if self.age_checkbox.isChecked():
            age_label = QLabel("Age:")
            age_input = QSpinBox()
            age_input.setRange(0, 120)  # Age range
            self.form_layout.addRow(age_label, age_input)

        if self.gender_checkbox.isChecked():
            gender_label = QLabel("Gender:")
            gender_input = QComboBox()
            gender_input.addItems(["Select", "Male", "Female", "Other"])
            self.form_layout.addRow(gender_label, gender_input)

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
                background-color: #121212;
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
                border: 1px solid #333;
                border-radius: 4px;
                padding: 5px;
                background-color: #1e1e1e;
                color: #ffffff;
            }
            QLineEdit:hover, QComboBox:hover, QSpinBox:hover {
                border: 1px solid #6200ea;
            }
            QLineEdit:focus, QComboBox:focus, QSpinBox:focus {
                border: 1px solid #bb86fc;
            }
            QPushButton {
                background-color: #6200ea;
                color: white;
                border: none;
                border-radius: 4px;
                padding: 10px;
                font-size: 14px;
            }
            QPushButton:hover {
                background-color: #3700b3;
            }
            QPushButton:pressed {
                background-color: #bb86fc;
            }
            QCheckBox {
                padding: 5px;
                color: #e0e0e0;
            }
            QCheckBox::indicator {
                width: 15px;
                height: 15px;
                background-color: #333;
                border: 1px solid #777;
                border-radius: 2px;
            }
            QCheckBox::indicator:checked {
                background-color: #6200ea;
                border: 1px solid #bb86fc;
            }
        """)