import os, sys
import zazzle
from tqdm import tqdm
import shutil
from utilities import SB_ASCII, SB_FILES, SB_VIDEO, SB_PROBE, log
from gui import SB_Main_Window
from PyQt6.QtWidgets import QApplication

# Initialize logging
zazzle.ZZ_Init.configure_logger(file_name="starboard")
log = zazzle.ZZ_Logging.log

if __name__ == "__main__":
    # Console blurb because go big or go home amirite
    SB_ASCII.print_intro_consol_blurb(text="STARBOARD", font="doom")
    print()

    # Step 2: Create the application object
    app = QApplication([])

    # Step 3: Create the main window
    window = SB_Main_Window()
    window.show()

    # Step 4: Start the application's event loop
    app.exec()