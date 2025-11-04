import os
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.backends import default_backend
from django.conf import settings

def generate_key(password: str, salt: bytes = None) -> tuple:
    """Generate an encryption key from a password using PBKDF2."""
    if salt is None:
        salt = os.urandom(16)
    
    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=32,
        salt=salt,
        iterations=100000,
        backend=default_backend()
    )
    key = kdf.derive(password.encode())
    return key, salt

def encrypt_file(file_data: bytes, password: str) -> tuple:
    """Encrypt file data using AES-256-CBC."""
    key, salt = generate_key(password)
    iv = os.urandom(16)
    
    cipher = Cipher(
        algorithms.AES(key),
        modes.CBC(iv),
        backend=default_backend()
    )
    encryptor = cipher.encryptor()
    
    # Add padding to make the data length a multiple of 16
    padding_length = 16 - (len(file_data) % 16)
    padded_data = file_data + bytes([padding_length] * padding_length)
    
    encrypted_data = encryptor.update(padded_data) + encryptor.finalize()
    return encrypted_data, salt, iv

def decrypt_file(encrypted_data: bytes, password: str, salt: bytes, iv: bytes) -> bytes:
    """Decrypt file data using AES-256-CBC."""
    key, _ = generate_key(password, salt)
    
    cipher = Cipher(
        algorithms.AES(key),
        modes.CBC(iv),
        backend=default_backend()
    )
    decryptor = cipher.decryptor()
    
    decrypted_data = decryptor.update(encrypted_data) + decryptor.finalize()
    
    # Remove padding
    padding_length = decrypted_data[-1]
    return decrypted_data[:-padding_length]

def save_encrypted_file(file_data: bytes, password: str, filename: str) -> tuple:
    """Save an encrypted file and return its path and metadata."""
    encrypted_data, salt, iv = encrypt_file(file_data, password)
    
    # Generate a unique filename
    encrypted_filename = f"{os.urandom(8).hex()}_{filename}"
    file_path = os.path.join(settings.ENCRYPTED_FILES_ROOT, encrypted_filename)
    
    # Ensure the directory exists
    os.makedirs(settings.ENCRYPTED_FILES_ROOT, exist_ok=True)
    
    # Save the encrypted file
    with open(file_path, 'wb') as f:
        f.write(encrypted_data)
    
    return encrypted_filename, salt, iv

def get_decrypted_file(file_path: str, password: str, salt: bytes, iv: bytes) -> bytes:
    """Read and decrypt a file."""
    with open(os.path.join(settings.ENCRYPTED_FILES_ROOT, file_path), 'rb') as f:
        encrypted_data = f.read()
    
    return decrypt_file(encrypted_data, password, salt, iv) 