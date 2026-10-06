import hashlib
from datetime import datetime
from database.connection import get_db_connection
from database.models import CREATE_TABLES_SQL

class AccountRepository:
    
    @staticmethod
    def initialize_db():
        with get_db_connection() as conn:
            conn.executescript(CREATE_TABLES_SQL)

    @staticmethod
    def save_master_config(verification_hash: str, salt_hex: str):
        # first run master password setup
        with get_db_connection() as conn:
            conn.execute(
                "INSERT INTO master_config (verification_hash, crypto_salt) VALUES (?, ?);",
                (verification_hash, salt_hex)
            )

    @staticmethod
    def get_master_config():
        with get_db_connection() as conn:
            row = conn.execute("SELECT verification_hash, crypto_salt FROM master_config LIMIT 1;").fetchone()
            return dict(row) if row else None

    @staticmethod
    def add_account(title: str, url: str, encrypted_login: str, encrypted_pass: str, raw_pass_text: str):
        md5_hash = hashlib.md5(raw_pass_text.encode()).hexdigest()
        pass_len = len(raw_pass_text)
        
        with get_db_connection() as conn:
            conn.execute(
                """INSERT INTO accounts 
                   (title, url, login, encrypted_password, password_length, password_hash_md5) 
                   VALUES (?, ?, ?, ?, ?, ?);""",
                (title, url, encrypted_login, encrypted_pass, pass_len, md5_hash)
            )

    @staticmethod
    def get_all_short_accounts():
        with get_db_connection() as conn:
            rows = conn.execute("SELECT id, title FROM accounts ORDER BY title ASC;").fetchall()
            return [dict(r) for r in rows]

    @staticmethod
    def get_account_by_id(account_id: int):
        with get_db_connection() as conn:
            row = conn.execute("SELECT * FROM accounts WHERE id = ?;", (account_id,)).fetchone()
            return dict(row) if row else None

    @staticmethod
    def delete_account(account_id: int):
        with get_db_connection() as conn:
            conn.execute("DELETE FROM accounts WHERE id = ?;", (account_id,))
