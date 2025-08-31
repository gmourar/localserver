import base64
import os
import re
from hashlib import sha256
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.primitives import padding
from cryptography.hazmat.backends import default_backend
from config import SECRET_KEY

def encrypt_cpf(cpf: str) -> str:
    iv = os.urandom(16)
    key_hex = sha256(SECRET_KEY.encode('utf-8')).hexdigest()
    key = key_hex[:32].encode('ascii')

    padder = padding.PKCS7(128).padder()
    padded_data = padder.update(cpf.encode('utf-8')) + padder.finalize()

    cipher = Cipher(algorithms.AES(key), modes.CBC(iv), backend=default_backend())
    encryptor = cipher.encryptor()
    ciphertext = encryptor.update(padded_data) + encryptor.finalize()

    ct_b64 = base64.b64encode(ciphertext).decode('ascii')
    combined = iv + ct_b64.encode('ascii')
    return base64.b64encode(combined).decode('ascii')

def decrypt_cpf(encrypted_base64: str) -> str:
    raw = base64.b64decode(encrypted_base64)
    iv, ct_b64_ascii = raw[:16], raw[16:]
    ciphertext = base64.b64decode(ct_b64_ascii)

    key_hex_ascii = sha256(SECRET_KEY.encode('utf-8')).hexdigest().encode('ascii')
    key = key_hex_ascii[:32]

    cipher = Cipher(algorithms.AES(key), modes.CBC(iv), backend=default_backend())
    decryptor = cipher.decryptor()
    padded = decryptor.update(ciphertext) + decryptor.finalize()

    unpadder = padding.PKCS7(128).unpadder()
    data = unpadder.update(padded) + unpadder.finalize()

    return data.decode('utf-8')

def formatar_cpf(cpf: str) -> str:
    return re.sub(r'\D', '', cpf)
