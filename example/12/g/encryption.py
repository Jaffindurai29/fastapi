from cryptography.fernet import Fernet

from config import FERNET_KEY

# One Fernet object for the whole app. Fernet = AES encryption plus a
# signature, so a tampered or wrong-key value fails loudly instead of
# decrypting to garbage.
fernet = Fernet(FERNET_KEY)


def encrypt(plaintext: str) -> str:
    # Fernet works on bytes: str -> bytes -> encrypted bytes -> str for the
    # Text column. The result is URL-safe base64, so it stores fine.
    return fernet.encrypt(plaintext.encode()).decode()


def decrypt(ciphertext: str) -> str:
    # Raises cryptography.fernet.InvalidToken if the key is wrong or the
    # value was tampered with. main.py turns that into a 500.
    return fernet.decrypt(ciphertext.encode()).decode()
