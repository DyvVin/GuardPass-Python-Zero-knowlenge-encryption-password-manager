import hashlib
from database.repository import AccountRepository
from crypto.key_derivation import derive_key, generate_salt

class AuthService:
    _SESSION_KEY: bytes = None

    @classmethod
    def get_crypto_key(cls) -> bytes:
        if cls._SESSION_KEY is None:
            raise PermissionError("Access denied: Session key invalid")
        return cls._SESSION_KEY

    @classmethod
    def authenticate(cls, master_password: str) -> bool:
        AccountRepository.initialize_db()
        
        config = AccountRepository.get_master_config()
        
        current_password_hash = hashlib.sha256(master_password.encode()).hexdigest()

        if config is None:
            # first run scenario
            salt = generate_salt()
            AccountRepository.save_master_config(current_password_hash, salt.hex())
            
            cls._SESSION_KEY = derive_key(master_password, salt)
            return True
            
        if config["verification_hash"] == current_password_hash:
            salt = bytes.fromhex(config["crypto_salt"])
            cls._SESSION_KEY = derive_key(master_password, salt)
            return True
            
        return False 
