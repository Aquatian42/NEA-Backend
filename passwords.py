import bcrypt

def hash_password(pwd):
    password = pwd.encode("utf-8")
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(password, salt)
    return hashed

def verify_password(plain_password: str, hashed_password: str):                                        
    return bcrypt.checkpw(plain_password.encode('utf-8'),hashed_password)                                      