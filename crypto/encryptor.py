import base64
from cryptography.hazmat.primitives.ciphers.aead import AESGCM

import os
import base64
from cryptography.hazmat.primitives.ciphers.aead import AESGCM

def encrypt_data(plain_text: str, secret_key: bytes) -> str:
    if not plain_text:
        return ""
    
    aesgcm = AESGCM(secret_key)
    
    nonce = os.urandom(12) 
    encrypted_bytes = aesgcm.encrypt(nonce, plain_text.encode(), None)
    result = nonce + encrypted_bytes
    
    return base64.b64encode(result).decode('utf-8')


def decrypt_data(cipher_text_base64: str, secret_key: bytes) -> str:
    if not cipher_text_base64:
        return ""
    
    aesgcm = AESGCM(secret_key)
    
    raw_data = base64.b64decode(cipher_text_base64.encode('utf-8'))

    nonce = raw_data[:12]
    encrypted_bytes = raw_data[12:]
    
    decrypted_bytes = aesgcm.decrypt(nonce, encrypted_bytes, None)
    return decrypted_bytes.decode('utf-8')
