"""
Token Encryption Service

Serviço de criptografia para proteger tokens OAuth dos instrutores.
Usa Fernet (AES-128-CBC + HMAC) do pacote `cryptography`.
"""

import base64
import hashlib

from cryptography.fernet import Fernet

from src.infrastructure.config import settings


def _derive_key(secret: str) -> bytes:
    """Deriva uma chave Fernet de 32 bytes a partir de um segredo."""
    digest = hashlib.sha256(secret.encode()).digest()
    return base64.urlsafe_b64encode(digest)


def _get_fernet() -> Fernet:
    """Retorna instância Fernet com a chave de criptografia."""
    key = _derive_key(settings.encryption_key)
    return Fernet(key)


def encrypt_token(plaintext: str) -> str:
    """
    Criptografa um token OAuth.

    Args:
        plaintext: Token em texto plano.

    Returns:
        Token criptografado em base64.
    """
    fernet = _get_fernet()
    return fernet.encrypt(plaintext.encode()).decode()


def decrypt_token(ciphertext: str) -> str:
    """
    Descriptografa um token OAuth.

    Args:
        ciphertext: Token criptografado em base64.

    Returns:
        Token em texto plano.
    """
    fernet = _get_fernet()
    return fernet.decrypt(ciphertext.encode()).decode()
