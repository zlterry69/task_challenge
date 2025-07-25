from src.infrastructure.auth import ACCESS_TOKEN_EXPIRE_MINUTES, ALGORITHM, pwd_context


def test_bcrypt_context():
    assert pwd_context is not None
    test_password = "test123"
    hashed = pwd_context.hash(test_password)
    assert pwd_context.verify(test_password, hashed)


def test_auth_constants():
    assert ALGORITHM == "HS256"
    assert ACCESS_TOKEN_EXPIRE_MINUTES == 60


def test_password_context_different_hashes():
    password = "same_password"
    hash1 = pwd_context.hash(password)
    hash2 = pwd_context.hash(password)
    # Bcrypt should generate different hashes for same password due to salt
    assert hash1 != hash2
    # But both should verify correctly
    assert pwd_context.verify(password, hash1)
    assert pwd_context.verify(password, hash2)
