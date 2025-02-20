from Crypto.Cipher import AES
from Crypto.Util.Padding import pad, unpad
import base64
import hashlib

# Secret key (must be 16, 24, or 32 bytes)
SECRET_KEY = "your_secure_key_123"  # Change this to something strong


def get_key():
    """Generate a 32-byte key using SHA-256"""
    return hashlib.sha256(SECRET_KEY.encode()).digest()


def encrypt_message(message):
    """Encrypt message using AES"""
    key = get_key()
    cipher = AES.new(key, AES.MODE_ECB)

    # Pad message to block size (16 bytes) for AES encryption
    message_bytes = message.encode('utf-8')  # Support for emojis
    padded_message = pad(message_bytes, AES.block_size)

    encrypted_bytes = cipher.encrypt(padded_message)
    return base64.b64encode(encrypted_bytes).decode()


def decrypt_message(encrypted_message):
    """Decrypt message using AES"""
    key = get_key()
    cipher = AES.new(key, AES.MODE_ECB)

    decrypted_bytes = cipher.decrypt(base64.b64decode(encrypted_message))

    # Unpad decrypted bytes and decode back to string
    decrypted_message = unpad(decrypted_bytes, AES.block_size).decode('utf-8')
    return decrypted_message
