import os
import json
import base64
import getpass

from pathlib import Path
from typing import Final
from cryptography.hazmat.primitives.ciphers.aead import AESGCM  # used for Encryption
from argon2.low_level import (
    hash_secret_raw,
    Type,
)  # Hashing ( we are not using sha256 or md5 because of GPU brute-force risks )

from constants import (
    SALT_LENGTH_BYTES,
    NONCE_LENGTH_BYTES,
    ARGON2_TIME_COST,
    ARGON2_MEMORY_KIB,
    ARGON2_PARALLELISM,
    VAULT_FORMAT_VERSION,
    VAULT_KEY_VERSION,
    VAULT_KEY_KDF,
    VAULT_KEY_CIPHER,
    KDF_KEY_NAME,
    KDF_KEY_SALT,
    CIPHER_KEY_NAME,
    CIPHER_KEY_NONCE,
    CIPHER_KEY_CIPHERTEXT,
    KDF_NAME_ARGON2ID,
    CIPHER_NAME_AES_256_GCM,
    DEFAULT_VAULT_DIRECTORY,
    DEFAULT_VAULT_PATH,
    VAULT_FILE_MODE,
    MSG_VAULT_ALREADY_EXISTS,
    MSG_VAULT_CREATED,
    PROMPT_MASTER_PASSWORD,
    PROMPT_MASTER_PASSWORD_CONFIRM,
    PROMPT_MASTER_PASSWORD_NEW,
)


def derive_key(master_password: str, salt: bytes) -> bytes:
    return hash_secret_raw(
        secret=master_password.encode(),
        salt=salt,
        time_cost=ARGON2_TIME_COST,
        memory_cost=ARGON2_MEMORY_KIB,
        parallelism=ARGON2_PARALLELISM,
        hash_len=32,
        type=Type.ID,
    )


def vault_exists() -> bool:
    return DEFAULT_VAULT_PATH.exists()


def create_vault() -> Path:
    master_password: str = getpass.getpass(PROMPT_MASTER_PASSWORD)
    if vault_exists():
        raise FileExistsError(MSG_VAULT_ALREADY_EXISTS.format(path=DEFAULT_VAULT_PATH))

    DEFAULT_VAULT_DIRECTORY.mkdir(parents=True, exist_ok=True)

    salt = os.urandom(SALT_LENGTH_BYTES)
    key = derive_key(master_password, salt)

    nonce = os.urandom(NONCE_LENGTH_BYTES)
    plaintext = json.dumps({}).encode()
    ciphertext = AESGCM(key).encrypt(nonce, plaintext, None)

    vault = {
        VAULT_KEY_VERSION: VAULT_FORMAT_VERSION,
        VAULT_KEY_KDF: {
            KDF_KEY_NAME: KDF_NAME_ARGON2ID,
            KDF_KEY_SALT: base64.b64encode(salt).decode(),
        },
        VAULT_KEY_CIPHER: {
            CIPHER_KEY_NAME: CIPHER_NAME_AES_256_GCM,
            CIPHER_KEY_NONCE: base64.b64encode(nonce).decode(),
            CIPHER_KEY_CIPHERTEXT: base64.b64encode(ciphertext).decode(),
        },
    }

    DEFAULT_VAULT_PATH.write_text(json.dumps(vault, indent=2))
    DEFAULT_VAULT_PATH.chmod(VAULT_FILE_MODE)

    return DEFAULT_VAULT_PATH
