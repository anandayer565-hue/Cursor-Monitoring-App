"""Unit tests for password hashing helpers (Step 1.1)."""

import pytest

from app.auth_utils import check_password, hash_password


def test_hash_password_returns_bcrypt_string():
    hashed = hash_password("admin")
    assert isinstance(hashed, str)
    assert hashed.startswith("$2")  # bcrypt prefix


def test_check_password_match():
    hashed = hash_password("admin")
    assert check_password("admin", hashed) is True


def test_check_password_mismatch():
    hashed = hash_password("admin")
    assert check_password("wrong", hashed) is False


def test_hash_password_rejects_empty():
    with pytest.raises(ValueError):
        hash_password("")


def test_check_password_empty_inputs():
    hashed = hash_password("admin")
    assert check_password("", hashed) is False
    assert check_password("admin", "") is False


def test_check_password_invalid_hash_returns_false():
    assert check_password("admin", "not-a-valid-hash") is False
