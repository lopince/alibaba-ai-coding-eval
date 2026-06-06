import unittest
from unittest.mock import MagicMock, patch
from app.models.database import User


class TestUserModel(unittest.TestCase):
    def test_user_creation(self):
        user = User(username="alice", email="alice@test.com", full_name="Alice", password_hash="abc123")
        self.assertEqual(user.username, "alice")
        self.assertEqual(user.email, "alice@test.com")

    def test_user_no_full_name(self):
        user = User(username="bob", email="bob@test.com", password_hash="abc123")
        self.assertIsNone(user.full_name)


class TestUserSchema(unittest.TestCase):
    def test_valid_user_create(self):
        from app.schemas.schemas import UserCreateSchema
        schema = UserCreateSchema()
        data = schema.load({
            "username": "alice",
            "email": "alice@test.com",
            "password": "securepass123",
        })
        self.assertEqual(data["username"], "alice")

    def test_short_username_rejected(self):
        from app.schemas.schemas import UserCreateSchema
        from marshmallow import ValidationError
        schema = UserCreateSchema()
        with self.assertRaises(ValidationError):
            schema.load({"username": "ab", "email": "a@b.com", "password": "securepass123"})

    def test_short_password_rejected(self):
        from app.schemas.schemas import UserCreateSchema
        from marshmallow import ValidationError
        schema = UserCreateSchema()
        with self.assertRaises(ValidationError):
            schema.load({"username": "alice", "email": "a@b.com", "password": "short"})


if __name__ == "__main__":
    unittest.main()
