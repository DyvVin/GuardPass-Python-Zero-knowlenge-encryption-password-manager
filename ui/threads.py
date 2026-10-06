from PyQt6.QtCore import QThread, pyqtSignal

from database.repository import AccountRepository
from services.auth_service import AuthService
from services.auditor import PasswordAuditor
from crypto.encryptor import encrypt_data, decrypt_data


class AuthWorkerThread(QThread):
    # bg thread for master password
    # prevents interface freezing during (possibly) intensive PBKDF2 hashing (100,000 iterations)
    result_ready = pyqtSignal(bool)

    def __init__(self, master_password: str):
        super().__init__()
        self.master_password = master_password

    def run(self):
        success = AuthService.authenticate(self.master_password)
        self.result_ready.emit(success)


class DataLoaderWorkerThread(QThread):
    data_loaded = pyqtSignal(dict)

    def run(self):
        accounts = AccountRepository.get_all_short_accounts()
        
        audit_results = PasswordAuditor.run_security_audit()
        
        self.data_loaded.emit({
            "accounts": accounts,
            "audit": audit_results
        })


class AccountDetailsWorkerThread(QThread):
    # AES-256
    details_ready = pyqtSignal(dict)

    def __init__(self, account_id: int):
        super().__init__()
        self.account_id = account_id

    def run(self):
        account = AccountRepository.get_account_by_id(self.account_id)
        
        if account:
            try:
                crypto_key = AuthService.get_crypto_key()
                
                account["decrypted_login"] = decrypt_data(account["login"], crypto_key)
                account["decrypted_password"] = decrypt_data(account["encrypted_password"], crypto_key)
            except Exception as e:
                account["decrypted_login"] = "Decryption error"
                account["decrypted_password"] = "Session key error"
        
        self.details_ready.emit(account)


class AddAccountWorkerThread(QThread):
    # AES-256-GCM 
    save_success = pyqtSignal()

    def __init__(self, title: str, url: str, raw_login: str, raw_password: str):
        super().__init__()
        self.title = title
        self.url = url
        self.raw_login = raw_login
        self.raw_password = raw_password

    def run(self):
        crypto_key = AuthService.get_crypto_key()
        
        encrypted_login = encrypt_data(self.raw_login, crypto_key)
        encrypted_password = encrypt_data(self.raw_password, crypto_key)
        
        AccountRepository.add_account(
            title=self.title,
            url=self.url,
            encrypted_login=encrypted_login,
            encrypted_pass=encrypted_password,
            raw_pass_text=self.raw_password # only used for length and MD5 calculation inside SQL
        )
        
        self.save_success.emit()
