from PyQt6.QtWidgets import (QMainWindow, QWidget, QHBoxLayout, QVBoxLayout, 
                             QListWidget, QListWidgetItem, QLabel, QPushButton, 
                             QProgressBar, QLineEdit, QDialog, QFormLayout, QMessageBox)
from PyQt6.QtCore import Qt
import sys
import secrets
import string

from .styles import MAIN_THEME_STYLE
from .threads import DataLoaderWorkerThread, AccountDetailsWorkerThread, AddAccountWorkerThread, UpdatePasswordWorkerThread
from database.repository import AccountRepository
from services.auditor import PasswordAuditor

class AccountListWidgetItem(QWidget):
    def __init__(self, account_id: int, title: str, parent_window):
        super().__init__()
        self.account_id = account_id
        self.title = title
        self.parent_window = parent_window
        self.init_ui()

    def init_ui(self):
        import os
        from PyQt6.QtGui import QPixmap
        
        layout = QHBoxLayout(self)
        layout.setContentsMargins(5, 5, 5, 5)
        layout.setSpacing(5)

        self.label = QLabel(self.title)
        layout.addWidget(self.label, stretch=1)

        try:
            account_data = AccountRepository.get_account_by_id(self.account_id)
            from services.auth_service import AuthService
            from crypto.encryptor import decrypt_data
            
            crypto_key = AuthService.get_crypto_key()
            plain_password = decrypt_data(account_data["encrypted_password"], crypto_key)
            
            if PasswordAuditor.check_if_password_is_weak(plain_password):
                def resource_path(relative_path):
                    try:
                        base_path = sys._MEIPASS
                    except Exception:
                        base_path = os.path.abspath(".")

                    return os.path.join(base_path, relative_path)
                icon_path = resource_path("icons/attention.ico")
                
                if os.path.exists(icon_path):
                    lbl_icon = QLabel()
                    pixmap = QPixmap(icon_path)
                    lbl_icon.setPixmap(pixmap.scaled(16, 16, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation))
                    lbl_icon.setToolTip("Warning: This account uses a weak password!")
                    layout.addWidget(lbl_icon)
        except Exception:
            pass

        # Кнопка Изменить (Перо)
        self.btn_edit = QPushButton("Edit")
        self.btn_edit.setObjectName("listActionButton")
        self.btn_edit.setToolTip("Edit account")
        self.btn_edit.clicked.connect(self.on_edit_clicked)
        layout.addWidget(self.btn_edit)

        # Кнопка Удалить (Корзина)
        self.btn_delete = QPushButton("Wipe")
        self.btn_delete.setObjectName("listActionButton")
        self.btn_delete.setToolTip("Delete account")
        self.btn_delete.clicked.connect(self.on_delete_clicked)
        layout.addWidget(self.btn_delete)

    def on_edit_clicked(self):
        dialog = QDialog(self.parent_window)
        dialog.setWindowTitle(f"Edit {self.title}")
        dialog.setStyleSheet(MAIN_THEME_STYLE)
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
        box.setStyleSheet(MAIN_THEME_STYLE)
        
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
        self.resize(950, 600)
        self.setStyleSheet(MAIN_THEME_STYLE)
        
        self.all_cached_accounts = []
        self.current_selected_account_id = None
        self.generated_secure_password = ""
        self.init_ui()

    def init_ui(self):
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        main_layout = QHBoxLayout(central_widget)
        main_layout.setContentsMargins(15, 15, 15, 15)
        main_layout.setSpacing(15)

        left_panel = QVBoxLayout()
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Search by service name...")
        self.search_input.textChanged.connect(self.filter_accounts)
        left_panel.addWidget(self.search_input)

        self.account_list = QListWidget()
        self.account_list.currentRowChanged.connect(self.load_account_details)
        left_panel.addWidget(self.account_list)
        
        btn_add = QPushButton("+ Add Service")
        btn_add.clicked.connect(self.open_add_dialog)
        left_panel.addWidget(btn_add)
        
        main_layout.addLayout(left_panel, stretch=14)

        right_panel = QVBoxLayout()
        right_panel.setSpacing(15)

        audit_box = QVBoxLayout()
        audit_title = QLabel("Database Security Audit")
        audit_title.setObjectName("titleLabel")
        audit_box.addWidget(audit_title)
        
        self.progress_label = QLabel("Password Strength: 100%")
        audit_box.addWidget(self.progress_label)
        
        self.progress_bar = QProgressBar()
        self.progress_bar.setValue(100)
        audit_box.addWidget(self.progress_bar)
        
        self.audit_details_label = QLabel("Total accounts: 0")
        self.audit_details_label.setStyleSheet("color: #555555; font-size: 12px;")
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
        
        self.lbl_warning = QLabel("Warning: This password is weak and vulnerable!")
        self.lbl_warning.setStyleSheet("font-weight: bold; margin-top: 5px;")
        self.lbl_warning.hide()
        details_box.addWidget(self.lbl_warning)
        
        self.btn_trigger_generator = QPushButton("Generate Secure Password")
        self.btn_trigger_generator.clicked.connect(self.start_password_generation_flow)
        self.btn_trigger_generator.hide()
        details_box.addWidget(self.btn_trigger_generator)
        
        self.generator_widget = QWidget()
        gen_layout = QVBoxLayout(self.generator_widget)
        gen_layout.setContentsMargins(0, 5, 0, 5)
        
        self.lbl_new_password_proposal = QLabel("Proposed secure password: —")
        self.lbl_new_password_proposal.setStyleSheet("font-weight: bold; color: #726DA8; font-size: 15px;")
        gen_layout.addWidget(self.lbl_new_password_proposal)
        
        choice_layout = QHBoxLayout()
        self.btn_accept_pass = QPushButton("Accept new password")
        self.btn_accept_pass.clicked.connect(self.accept_generated_password)
        self.btn_reject_pass = QPushButton("Cancel")
        self.btn_reject_pass.clicked.connect(self.hide_generator_flow)
        self.btn_reject_pass.setObjectName("listDeleteButton")
        
        self.btn_regenerate_pass = QPushButton("Generate again")
        self.btn_regenerate_pass.clicked.connect(self.generate_and_display_new_password)
        
        choice_layout.addWidget(self.btn_accept_pass)
        choice_layout.addWidget(self.btn_regenerate_pass)
        choice_layout.addWidget(self.btn_reject_pass)
        gen_layout.addLayout(choice_layout)
        
        self.generator_widget.hide()
        details_box.addWidget(self.generator_widget)
        
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
            f"Total Accounts: {audit['total_accounts']} | Weak (by 4 metrics): {audit['weak_passwords']} | Reused: {audit['reused_passwords']}"
        )

    def filter_accounts(self):
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

        self.hide_generator_flow()
        self.details_title.setText("Account Details: —")
        self.lbl_login.setText("Login: —")
        self.lbl_password.setText("Password: —")
        self.lbl_warning.hide()
        self.btn_trigger_generator.hide()

    def load_account_details(self, current_row: int):
        if current_row < 0:
            return
        item = self.account_list.item(current_row)
        if not item:
            return
            
        self.current_selected_account_id = item.data(Qt.ItemDataRole.UserRole)

        self.hide_generator_flow()
        self.details_thread = AccountDetailsWorkerThread(self.current_selected_account_id)
        self.details_thread.details_ready.connect(self.on_details_ready)
        self.details_thread.start()
    
    def on_details_ready(self, account: dict):
        self.details_title.setText(f"Account Details: {account['title']}")
        self.lbl_login.setText(f"Login: {account['decrypted_login']}")
        raw_password = account['decrypted_password']
        self.lbl_password.setText(f"Password: {raw_password}")
        if PasswordAuditor.check_if_password_is_weak(raw_password):
            self.lbl_warning.show()
            self.btn_trigger_generator.show()
        else:
            self.lbl_warning.hide()
            self.btn_trigger_generator.hide()
    
    def start_password_generation_flow(self):
        self.btn_trigger_generator.hide()
        self.generator_widget.show()
        self.generate_and_display_new_password()
    
    def generate_and_display_new_password(self):
        alphabet = string.ascii_letters + string.digits + "!@#$%^&*()_+-="
        while True:
            candidate = "".join(secrets.choice(alphabet) for _ in range(14))
            if not PasswordAuditor.check_if_password_is_weak(candidate):
                self.generated_secure_password = candidate
                break
        self.lbl_new_password_proposal.setText(f"Proposed secure password: {self.generated_secure_password}")

    def accept_generated_password(self):
        if not self.current_selected_account_id:
            return
        self.update_thread = UpdatePasswordWorkerThread(
            self.current_selected_account_id,
            self.generated_secure_password,
        )
        self.update_thread.update_success.connect(self.on_password_update_success)
        self.update_thread.start()

    def on_password_update_success(self):
        self.hide_generator_flow()
        QMessageBox.information(self, "Success", "Password updated and safely database-stored!")
        self.refresh_data()

    def hide_generator_flow(self):
        self.generator_widget.hide()
        self.generated_secure_password = ""
        if self.lbl_warning.isVisible():
            self.btn_trigger_generator.show()

    def open_add_dialog(self):
        dialog = QDialog(self)
        dialog.setWindowTitle("Add Account")
        dialog.setStyleSheet(MAIN_THEME_STYLE)
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