import hashlib
import os


def _keystream(key: bytes, nonce: bytes, length: int):
    out = bytearray()
    counter = 0
    while len(out) < length:
        ctr = counter.to_bytes(4, "big")
        out.extend(hashlib.sha256(key + nonce + ctr).digest())
        counter += 1
    return bytes(out[:length])


def encrypt_bytes(data: bytes, passphrase: str = "fusion_key_2026") -> bytes:
    """Encrypt bytes with a deterministic keystream derived from passphrase.

    Format: nonce(12 bytes) || ciphertext
    """
    key = hashlib.sha256(passphrase.encode()).digest()
    nonce = os.urandom(12)
    ks = _keystream(key, nonce, len(data))
    ct = bytes(a ^ b for a, b in zip(data, ks))
    return nonce + ct


def decrypt_bytes(ciphertext: bytes, passphrase: str = "fusion_key_2026") -> bytes:
    if len(ciphertext) < 12:
        raise ValueError("ciphertext too short")
    key = hashlib.sha256(passphrase.encode()).digest()
    nonce = ciphertext[:12]
    ct = ciphertext[12:]
    ks = _keystream(key, nonce, len(ct))
    pt = bytes(a ^ b for a, b in zip(ct, ks))
    return pt
