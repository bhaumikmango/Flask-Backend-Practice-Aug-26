from pwdlib import PasswordHash

pwd_context = PasswordHash.recommended()

def hash(password : str):
    return pwd_context.hash(password)

def verify_pass(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)