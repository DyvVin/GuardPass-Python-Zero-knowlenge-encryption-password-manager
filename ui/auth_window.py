from PyQt6.QtWidgets import QDialog, QVBoxLayout, QLabel, QLineEdit, QPushButton, QHBoxLayout, QMessageBox
from PyQt6.QtCore import pyqtSignal

from .styles import DARK_THEME_STYLE
from .threads import AuthWorkerThread

class AuthWindow(QDialog):
    authenticated = pyqtSignal()

    def __init__(self):
        super().__init__()
        self.setWindowTitle("GuardPass — Authorization")
        self.setFixedSize(360, 240)
        self.setStyleSheet(DARK_THEME_STYLE)
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()
        layout.setSpacing(15)
        layout.setContentsMargins(30, 25, 30, 25)

        title = QLabel("System Login")
        title.setObjectName("titleLabel")
        layout.addWidget(title)

        self.info_label = QLabel("Enter your master password to unlock:")
        self.info_label.setStyleSheet("color: #A0A0A0; font-size: 12px;")
        layout.addWidget(self.info_label)

        self.password_input = QLineEdit()
        self.password_input.setPlaceholderText("Master Password")
        self.password_input.setEchoMode(QLineEdit.EchoMode.Password)
        layout.addWidget(self.password_input)

        btn_layout = QHBoxLayout()
        self.btn_login = QPushButton("Unlock")
        self.btn_login.clicked.connect(self.handle_auth)
        
        btn_layout.addWidget(self.btn_login)
        layout.addLayout(btn_layout)

        self.setLayout(layout)

    def handle_auth(self):
        password = self.password_input.text().strip()
        
        if not password:
            QMessageBox.warning(self, "Error", "Master password cannot be empty!")
            return

        self.btn_login.setEnabled(False)
        self.btn_login.setText("Checking...")

        self.auth_worker = AuthWorkerThread(password)
        self.auth_worker.result_ready.connect(self.on_auth_result)
        self.auth_worker.start()

    def on_auth_result(self, is_success: bool):
        self.btn_login.setEnabled(True)
        self.btn_login.setText("Unlock")

        if is_success:
            self.authenticated.emit()
            self.accept()
        else:
            QMessageBox.critical(self, "Access Denied", "Invalid master password!")
            self.password_input.clear()