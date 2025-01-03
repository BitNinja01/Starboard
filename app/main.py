import zazzle
from gui import SB_Main_Window
from PyQt6.QtWidgets import QApplication

# Initialize logging
zazzle.ZZ_Init.configure_logger(file_name="starboard")
log = zazzle.ZZ_Logging.log

if __name__ == "__main__":
    try:
        log(1, f"Creating application...")
        # Step 2: Create the application object
        app = QApplication([])

        # Step 3: Create the main window
        log(1, f"Creating main window...")
        window = SB_Main_Window()
        window.showMaximized()

        # Step 4: Start the application's event loop
        log(1, f"Starting program...")
        app.exec()
    except:
        log(4, f"CRITICAL ERROR")