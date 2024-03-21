from pwdlib import PasswordHash
from pwdlib.hashers.argon2 import Argon2Hasher

password_helper = PasswordHash((Argon2Hasher(),))
