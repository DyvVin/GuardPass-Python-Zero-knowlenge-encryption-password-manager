import string
from database.connection import get_db_connection
from crypto.encryptor import decrypt_data
from services.auth_service import AuthService

class PasswordAuditor:
    
    @staticmethod
    def check_if_password_is_weak(password: str) -> bool:
        if len(password) < 8:
            return True
            
        if not any(char.isdigit() for char in password):
            return True
            
        special_chars = "!@#$%^&*()_+-={}|;:,.<>?"
        if not any(char in special_chars for char in password):
            return True
            
        has_upper = any(char.isupper() for char in password)
        has_lower = any(char.islower() for char in password)
        if not (has_upper and has_lower):
            return True
            
        return False

    @staticmethod
    def run_security_audit() -> dict:
        metrics = {
            "total_accounts": 0,
            "weak_passwords": 0,
            "reused_passwords": 0,
            "security_score": 100
        }
        
        with get_db_connection() as conn:
            table_exists = conn.execute(
                "SELECT name FROM sqlite_master WHERE type='table' AND name='accounts';"
            ).fetchone()
            
            if not table_exists:
                return metrics 
                
            rows = conn.execute("SELECT id, encrypted_password, password_hash_md5 FROM accounts;").fetchall()
            metrics["total_accounts"] = len(rows)
            
            if metrics["total_accounts"] == 0:
                return metrics

        try:
            crypto_key = AuthService.get_crypto_key()
        except PermissionError:
            return metrics

        with get_db_connection() as conn:
            for row in rows:
                try:
                    plain_pass = decrypt_data(row["encrypted_password"], crypto_key)
                    if PasswordAuditor.check_if_password_is_weak(plain_pass):
                        metrics["weak_passwords"] += 1
                except Exception:
                    metrics["weak_passwords"] += 1

            dup_query = """
                SELECT SUM(cnt) as reused_total FROM (
                    SELECT COUNT(*) as cnt FROM accounts GROUP BY password_hash_md5 HAVING COUNT(*) > 1
                );
            """
            row_dup = conn.execute(dup_query).fetchone()
            metrics["reused_passwords"] = row_dup["reused_total"] if row_dup["reused_total"] else 0
            
            penalty = (metrics["weak_passwords"] * 15) + (metrics["reused_passwords"] * 10)
            metrics["security_score"] = max(0, 100 - penalty)
            
            return metrics
