import unittest
from app.schemas.schemas import CommentCreateSchema, CommentResponseSchema
from marshmallow import ValidationError


class TestCommentSchema(unittest.TestCase):
    def test_valid_comment_create(self):
        schema = CommentCreateSchema()
        data = schema.load({"body": "Great post!", "post_id": 1})
        self.assertEqual(data["body"], "Great post!")
        self.assertEqual(data["post_id"], 1)

    def test_empty_body_rejected(self):
        schema = CommentCreateSchema()
        with self.assertRaises(ValidationError):
            schema.load({"body": "", "post_id": 1})

    def test_body_too_long_rejected(self):
        schema = CommentCreateSchema()
        with self.assertRaises(ValidationError):
            schema.load({"body": "x" * 2001, "post_id": 1})

    def test_missing_post_id_rejected(self):
        schema = CommentCreateSchema()
        with self.assertRaises(ValidationError):
            schema.load({"body": "Some comment"})

    def test_comment_response(self):
        schema = CommentResponseSchema()
        result = schema.dump({
            "id": 1,
            "body": "Nice article",
            "post_id": 5,
            "author_id": 10
        })
        self.assertEqual(result["id"], 1)
        self.assertEqual(result["body"], "Nice article")
        self.assertEqual(result["post_id"], 5)
        self.assertEqual(result["author_id"], 10)


if __name__ == "__main__":
    unittest.main()
