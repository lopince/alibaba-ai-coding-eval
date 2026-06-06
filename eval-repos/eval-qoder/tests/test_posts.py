import unittest
from app.schemas.schemas import PostCreateSchema, PostResponseSchema
from marshmallow import ValidationError


class TestPostSchema(unittest.TestCase):
    def test_valid_post_create(self):
        schema = PostCreateSchema()
        data = schema.load({"title": "Hello World", "body": "Some body"})
        self.assertEqual(data["title"], "Hello World")

    def test_empty_title_rejected(self):
        schema = PostCreateSchema()
        with self.assertRaises(ValidationError):
            schema.load({"title": ""})

    def test_post_response(self):
        schema = PostResponseSchema()
        result = schema.dump({"id": 1, "title": "Test", "body": "Body", "author_id": 42})
        self.assertEqual(result["author_id"], 42)


if __name__ == "__main__":
    unittest.main()
