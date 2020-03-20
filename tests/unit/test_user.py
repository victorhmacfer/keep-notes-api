import pytest
from models.user import User


def test_sets_password():
    u = User(password='abc123')
    assert u.password_hash is not None


def test_password_getter_raises_error():
    u = User(password='abc123')
    with pytest.raises(AttributeError):
        u.password

def test_verify_password():
    u = User(password='abc123')
    assert u.verify_password('abc123') == True
    assert u.verify_password('wrong') == False




