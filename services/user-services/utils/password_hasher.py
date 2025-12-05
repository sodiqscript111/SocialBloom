import bcrypt

def hash_password(password: str) -> str:
    """Hashes a plaintext password using bcrypt."""
    hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
    return hashed_password.decode('utf-8')


def verify_password(password: str, hashed_password: str) -> bool:
    """Verifies if a plaintext password matches a hashed password."""
    return bcrypt.checkpw(password.encode('utf-8'), hashed_password.encode('utf-8'))
