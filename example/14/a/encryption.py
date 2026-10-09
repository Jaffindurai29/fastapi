from cryptography.fernet import Fernet

from config import FERNET_KEY

# Two-way. Used for data we must read again later: the phone and address
# on an order. Fernet = AES encryption plus a signature, so a tampered or
# wrong-key value fails loudly instead of decrypting to garbage.
fernet = Fernet(FERNET_KEY)


def encrypt(plaintext: str) -> str:
    # Like hashing, the same text gives a different result every time.
    return fernet.encrypt(plaintext.encode()).decode()


def decrypt(ciphertext: str) -> str:
    # Raises cryptography.fernet.InvalidToken if the key is wrong or the
    # value was tampered with.
    return fernet.decrypt(ciphertext.encode()).decode()
