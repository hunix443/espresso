import os
import json
import base64
import getpass

from pathlib import Path
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from argon2.low_level import (
    hash_secret_raw,
    Type,
)


def derive_key(master_password: str, salt: bytes) -> bytes:
    return hash_secret_raw(
        secret=master_password.encode(),
        salt=salt,
        time_cost=3,
        memory_cost=65536,
        parallelism=4,
        hash_len=32,
        type=Type.ID,
    )


def vault_exists() -> bool:
    return (Path.home() / ".espresso-vault" / "vault.json").exists()


def create_vault() -> Path:
    print("---Be Cautious---\n")
    master_password: str = getpass.getpass("Master password : ")
    vault_path = Path.home() / ".espresso-vault" / "vault.json"
    if vault_exists():
        raise FileExistsError(f"Vault already exists at {vault_path}")

    (Path.home() / ".espresso-vault").mkdir(parents=True, exist_ok=True)

    salt = os.urandom(16)
    key = derive_key(master_password, salt)

    nonce = os.urandom(12)
    plaintext = json.dumps({}).encode()
    ciphertext = AESGCM(key).encrypt(nonce, plaintext, None)

    vault = {
        "version": 1,
        "kdf": {
            "name": "argon2id",
            "salt": base64.b64encode(salt).decode(),
        },
        "cipher": {
            "name": "aes-256-gcm",
            "nonce": base64.b64encode(nonce).decode(),
            "ciphertext": base64.b64encode(ciphertext).decode(),
        },
    }

    vault_path.write_text(json.dumps(vault, indent=2))
    vault_path.chmod(0o600)

    return vault_path


def load_and_decrypt() -> tuple[dict, dict, bytes]:
    vault_path = Path.home() / ".espresso-vault" / "vault.json"
    vault = json.loads(vault_path.read_text())

    master_password = getpass.getpass("\nMaster password : ")
    salt = base64.b64decode(vault["kdf"]["salt"])
    key = derive_key(master_password, salt)

    nonce = base64.b64decode(vault["cipher"]["nonce"])
    ciphertext = base64.b64decode(vault["cipher"]["ciphertext"])

    try:
        plaintext = AESGCM(key).decrypt(nonce, ciphertext, None)
    except Exception:
        raise ValueError("Wrong master password (or vault file is corrupted)")

    entries = json.loads(plaintext.decode())
    return vault, entries, key


def encrypt_and_save(vault: dict, entries: dict, key: bytes) -> None:
    vault_path = Path.home() / ".espresso-vault" / "vault.json"

    nonce = os.urandom(12)
    plaintext = json.dumps(entries).encode()
    ciphertext = AESGCM(key).encrypt(nonce, plaintext, None)

    vault["cipher"]["nonce"] = base64.b64encode(nonce).decode()
    vault["cipher"]["ciphertext"] = base64.b64encode(ciphertext).decode()

    vault_path.write_text(json.dumps(vault, indent=2))
    vault_path.chmod(0o600)


def add_entry() -> None:
    vault, entries, key = load_and_decrypt()

    entry_name: str = input("Entry name: ")
    if entry_name in entries:
        print(f"Entry already exists: {entry_name}. Use --force to overwrite")
        return

    entry_username: str = input(f"Username for {entry_name}: ")
    entry_password: str = input(f"Password for {entry_name}: ")
    entry_url: str = input("URL (optional, press Enter to skip): ")
    entry_notes: str = input("Notes (optional, press Enter to skip): ")

    entry = {}
    if entry_username:
        entry["username"] = entry_username
    if entry_password:
        entry["password"] = entry_password
    if entry_url:
        entry["url"] = entry_url
    if entry_notes:
        entry["notes"] = entry_notes

    entries[entry_name] = entry
    encrypt_and_save(vault, entries, key)
    print(f"Added entry: {entry_name}")


def list_entries() -> None:
    vault, entries, key = load_and_decrypt()

    if not entries:
        print("[WARNING] Vault is empty")
        return

    print("---Entries---\n")
    for name in entries:
        print(f"[ENTRY] {name}")


def get_entry() -> None:
    vault, entries, key = load_and_decrypt()

    entry_name: str = input("Entry name: ")
    if entry_name not in entries:
        print(f"No entry named: {entry_name}")
        return

    entry = entries[entry_name]
    for field in ("username", "password", "url", "notes"):
        value = entry.get(field)
        if value:
            print(f"{field.capitalize()}: {value}")


def delete_entry() -> None:
    vault, entries, key = load_and_decrypt()

    entry_name: str = input("Entry name: ")
    if entry_name not in entries:
        print(f"No entry named: {entry_name}")
        return

    del entries[entry_name]
    encrypt_and_save(vault, entries, key)
    print(f"Deleted entry: {entry_name}")
