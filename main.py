import os
import sys
from PyQt6.QtWidgets import QApplication

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

from ui.auth_window import AuthWindow
from ui.main_window import MainWindow

def initialize_application_directory():
    app_data_root = os.environ.get("APPDATA") or os.path.expanduser("~")
    
    # Storing data in %AppData% folder
    app_folder = os.path.join(app_data_root, "GuardPass")
    
    if not os.path.exists(app_folder):
        os.makedirs(app_folder)
        #print(f"[INIT] App folder: {app_folder}")
    
    db_path = os.path.join(app_folder, "guardpass.db")
    #print(f"[INIT] DB path: {db_path}")
    
    os.environ["GUARDPASS_DB_PATH"] = db_path

def main():
    initialize_application_directory()

    # graphics initialization
    app = QApplication(sys.argv)

    auth_win = AuthWindow()
    main_win = MainWindow()

    auth_win.authenticated.connect(main_win.show)
    auth_win.show()

    sys.exit(app.exec())

if __name__ == "__main__":
    main()
