import unittest
from marshmallow import ValidationError
from app.schemas.schemas import CommentCreateSchema, CommentResponseSchema


class TestCommentCreateSchema(unittest.TestCase):
    def test_valid_comment_create(self):
        schema = CommentCreateSchema()
        data = schema.load({"post_id": 1, "content": "Nice post!"})
        self.assertEqual(data["post_id"], 1)
        self.assertEqual(data["content"], "Nice post!")

    def test_missing_post_id_rejected(self):
        schema = CommentCreateSchema()
        with self.assertRaises(ValidationError):
            schema.load({"content": "Nice post!"})

    def test_empty_content_rejected(self):
        schema = CommentCreateSchema()
        with self.assertRaises(ValidationError):
            schema.load({"post_id": 1, "content": ""})

    def test_missing_content_rejected(self):
        schema = CommentCreateSchema()
        with self.assertRaises(ValidationError):
            schema.load({"post_id": 1})


class TestCommentResponseSchema(unittest.TestCase):
    def test_comment_response(self):
        schema = CommentResponseSchema()
        result = schema.dump({
            "id": 1, "post_id": 2, "author_id": 3,
            "content": "Hello", "created_at": "2026-01-01T00:00:00+00:00",
        })
        self.assertEqual(result["id"], 1)
        self.assertEqual(result["post_id"], 2)
        self.assertEqual(result["author_id"], 3)
        self.assertEqual(result["content"], "Hello")


if __name__ == "__main__":
    unittest.main()
