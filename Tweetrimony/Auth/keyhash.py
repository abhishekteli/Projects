from enum import Enum
from .keys import Keys

class Hash(Enum):
    hash0 = Keys.encrypt_ah
    hash1 = Keys.encrypt_ac
    hash2 = Keys.encrypt_at
    hash3 = Keys.encrypt_as
    hash4 = Keys.encrypt_js
    hash5 = Keys.encrypt_es
