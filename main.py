import os
import json

from pathlib import Path

from constants import (
    DEFAULT_VAULT_FILENAME,
    DEFAULT_VAULT_DIRECTORY
)
from vault import create_vault, vault_exists

if __name__ == "__main__":
    
    if not vault_exists:
        create_vault()

    # implement other methods here
    
        
