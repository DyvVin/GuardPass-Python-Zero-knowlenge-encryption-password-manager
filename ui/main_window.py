from PyQt6.QtWidgets import (QMainWindow, QWidget, QHBoxLayout, QVBoxLayout, 
                             QListWidget, QListWidgetItem, QLabel, QPushButton, 
                             QProgressBar, QLineEdit, QDialog, QFormLayout, QMessageBox)
from PyQt6.QtCore import Qt

from .styles import DARK_THEME_STYLE
from .threads import DataLoaderWorkerThread, AccountDetailsWorkerThread, AddAccountWorkerThread
from database.repository import AccountRepository

class AccountListWidgetItem(QWidget):
    def __init__(self, account_id: int, title: str, parent_window):
        super().__init__()
        self.account_id = account_id
        self.title = title
        self.parent_window = parent_window
        self.init_ui()

    def init_ui(self):
        layout = QHBoxLayout(self)
        layout.setContentsMargins(5, 5, 5, 5)
        layout.setSpacing(5)

        self.label = QLabel(self.title)
        layout.addWidget(self.label, stretch=1)

        self.btn_edit = QPushButton("Edit")
        self.btn_edit.setObjectName("listActionButton")
        self.btn_edit.setToolTip("Edit account")
        self.btn_edit.clicked.connect(self.on_edit_clicked)
        layout.addWidget(self.btn_edit)

        self.btn_delete = QPushButton("Wipe")
        self.btn_delete.setObjectName("listActionButton")
        self.btn_delete.setToolTip("Delete account")
        self.btn_delete.clicked.connect(self.on_delete_clicked)
        layout.addWidget(self.btn_delete)

    def on_edit_clicked(self):
        dialog = QDialog(self.parent_window)
        dialog.setWindowTitle(f"Edit {self.title}")
        dialog.setStyleSheet(DARK_THEME_STYLE)
        form = QFormLayout(dialog)
        
        inp_title = QLineEdit(self.title)
        inp_login = QLineEdit()
        inp_pass = QLineEdit()
        form.addRow("New Title:", inp_title)
        form.addRow("New Login / Email:", inp_login)
        form.addRow("New Password:", inp_pass)
        
        btn_save = QPushButton("Update")
        form.addRow(btn_save)
        
        def save_edit():
            if not inp_title.text().strip() or not inp_login.text().strip() or not inp_pass.text().strip():
                QMessageBox.warning(dialog, "Error", "All fields must be filled!")
                return
            AccountRepository.delete_account(self.account_id)
            self.parent_window.add_thread = AddAccountWorkerThread(
                inp_title.text().strip(), "", inp_login.text().strip(), inp_pass.text().strip()
            )
            self.parent_window.add_thread.save_success.connect(lambda: [dialog.accept(), self.parent_window.refresh_data()])
            self.parent_window.add_thread.start()

        btn_save.clicked.connect(save_edit)
        dialog.exec()

    def on_delete_clicked(self):
        box = QMessageBox(self.parent_window)
        box.setIcon(QMessageBox.Icon.Question)
        box.setWindowTitle("Confirmation")
        box.setText(f"Are you sure you want to delete the account details for {self.title}?")
        box.setStyleSheet(DARK_THEME_STYLE)
        
        yes_btn = box.addButton("Yes", QMessageBox.ButtonRole.YesRole)
        no_btn = box.addButton("No", QMessageBox.ButtonRole.NoRole)
        
        box.exec()
        
        if box.clickedButton() == yes_btn:
            AccountRepository.delete_account(self.account_id)
            self.parent_window.refresh_data()


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("GuardPass — Password Manager")
        self.resize(900, 550)
        self.setStyleSheet(DARK_THEME_STYLE)
        
        self.all_cached_accounts = []
        self.init_ui()

    def init_ui(self):
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        main_layout = QHBoxLayout(central_widget)
        main_layout.setContentsMargins(15, 15, 15, 15)
        main_layout.setSpacing(15)

        # left panel
        left_panel = QVBoxLayout()
        
        search_layout = QHBoxLayout()
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Search by service name...")
        self.search_input.textChanged.connect(self.filter_accounts)
        search_layout.addWidget(self.search_input)
        
        left_panel.addLayout(search_layout)

        self.account_list = QListWidget()
        self.account_list.currentRowChanged.connect(self.load_account_details)
        left_panel.addWidget(self.account_list)
        
        btn_add = QPushButton("+ Add Service")
        btn_add.clicked.connect(self.open_add_dialog)
        left_panel.addWidget(btn_add)
        
        main_layout.addLayout(left_panel, stretch=14)

        # right panel
        right_panel = QVBoxLayout()
        right_panel.setSpacing(20)

        # audit block
        audit_box = QVBoxLayout()
        audit_title = QLabel("Database Security Audit")
        audit_title.setStyleSheet("font-weight: bold; color: #726DA8;") # renovate
        audit_box.addWidget(audit_title)
        
        self.progress_label = QLabel("Password Strength: 100%")
        audit_box.addWidget(self.progress_label)
        
        self.progress_bar = QProgressBar()
        self.progress_bar.setValue(100)
        audit_box.addWidget(self.progress_bar)
        
        self.audit_details_label = QLabel("Total accounts: 0")
        self.audit_details_label.setStyleSheet("color: #888888; font-size: 12px;") # renovate
        audit_box.addWidget(self.audit_details_label)
        right_panel.addLayout(audit_box)

        details_box = QVBoxLayout()
        self.details_title = QLabel("Account Details: —")
        self.details_title.setObjectName("titleLabel")
        details_box.addWidget(self.details_title)
        
        self.lbl_login = QLabel("Login: —")
        self.lbl_password = QLabel("Password: —")
        
        details_box.addWidget(self.lbl_login)
        details_box.addWidget(self.lbl_password)
        right_panel.addLayout(details_box)
        
        right_panel.addStretch()
        main_layout.addLayout(right_panel, stretch=36)

    def showEvent(self, event):
        super().showEvent(event)
        self.refresh_data()

    def refresh_data(self):
        self.loader_thread = DataLoaderWorkerThread()
        self.loader_thread.data_loaded.connect(self.on_data_loaded)
        self.loader_thread.start()

    def on_data_loaded(self, data: dict):
        self.all_cached_accounts = data["accounts"]
        self.filter_accounts()

        audit = data["audit"]
        self.progress_bar.setValue(int(audit["security_score"]))
        self.progress_label.setText(f"Password Strength: {int(audit['security_score'])}%")
        self.audit_details_label.setText(
            f"Total Accounts: {audit['total_accounts']} | Weak: {audit['weak_passwords']} | Reused: {audit['reused_passwords']}"
        )

    def filter_accounts(self):
        """Фильтрует список аккаунтов на основе введенного текста"""
        self.account_list.clear()
        search_query = self.search_input.text().lower().strip()

        for acc in self.all_cached_accounts:
            if search_query and search_query not in acc["title"].lower():
                continue
                
            item = QListWidgetItem(self.account_list)
            row_widget = AccountListWidgetItem(acc["id"], acc["title"], self)
            
            item.setSizeHint(row_widget.sizeHint())
            self.account_list.setItemWidget(item, row_widget)
            item.setData(Qt.ItemDataRole.UserRole, acc["id"])

        self.details_title.setText("Account Details: —")
        self.lbl_login.setText("Login: —")
        self.lbl_password.setText("Password: —")

    def load_account_details(self, current_row: int):
        if current_row < 0:
            return
        item = self.account_list.item(current_row)
        if not item:
            return
            
        db_id = item.data(Qt.ItemDataRole.UserRole)
        self.details_thread = AccountDetailsWorkerThread(db_id)
        self.details_thread.details_ready.connect(self.on_details_ready)
        self.details_thread.start()

    def on_details_ready(self, account: dict):
        self.details_title.setText(f"Account Details: {account['title']}")
        self.lbl_login.setText(f"Login: {account['decrypted_login']}")
        self.lbl_password.setText(f"Password: {account['decrypted_password']}")

    def open_add_dialog(self):
        dialog = QDialog(self)
        dialog.setWindowTitle("Add Account")
        dialog.setStyleSheet(DARK_THEME_STYLE)
        form = QFormLayout(dialog)

        inp_title = QLineEdit()
        inp_login = QLineEdit()
        inp_pass = QLineEdit()

        form.addRow("Service Name:", inp_title)
        form.addRow("Login / Email:", inp_login)
        form.addRow("Password:", inp_pass)

        btn_save = QPushButton("Save to Database")
        form.addRow(btn_save)

        def save_action():
            title = inp_title.text().strip()
            login = inp_login.text().strip()
            password = inp_pass.text().strip()

            if not title or not login or not password:
                QMessageBox.warning(dialog, "Error", "All fields must be filled!")
                return

            self.add_thread = AddAccountWorkerThread(title, "", login, password)
            self.add_thread.save_success.connect(lambda: [dialog.accept(), self.refresh_data()])
            self.add_thread.start()
            btn_save.clicked.connect(save_action)
            dialog.exec()