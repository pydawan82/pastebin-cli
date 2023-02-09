import os
from typing import Optional


def recover_key() -> Optional[str]:
    """Returns the API key from the environment variable PASTEBIN_API_KEY"""
    return os.environ.get('PASTEBIN_API_KEY', None)
