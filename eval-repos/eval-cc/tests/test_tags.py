import unittest
from app.schemas.schemas import TagCreate, TagResponse
from app.models.database import Tag
from pydantic import ValidationError


class TestTagSchema(unittest.TestCase):
    def test_valid_tag_create(self):
        tag = TagCreate(name="python", color="#3776AB")
        self.assertEqual(tag.name, "python")
        self.assertEqual(tag.color, "#3776AB")

    def test_lowercase_hex_accepted(self):
        tag = TagCreate(name="fastapi", color="#009688")
        self.assertEqual(tag.color, "#009688")

    def test_invalid_color_no_hash(self):
        with self.assertRaises(ValidationError):
            TagCreate(name="test", color="FF0000")

    def test_invalid_color_too_short(self):
        with self.assertRaises(ValidationError):
            TagCreate(name="test", color="#FFF")

    def test_invalid_color_too_long(self):
        with self.assertRaises(ValidationError):
            TagCreate(name="test", color="#FF0000FF")

    def test_invalid_color_not_hex(self):
        with self.assertRaises(ValidationError):
            TagCreate(name="test", color="#GGGGGG")

    def test_name_too_long_rejected(self):
        with self.assertRaises(ValidationError):
            TagCreate(name="x" * 51, color="#123456")

    def test_empty_name_rejected(self):
        with self.assertRaises(ValidationError):
            TagCreate(name="", color="#123456")

    def test_tag_response(self):
        tag_response = TagResponse(id=1, name="javascript", color="#F7DF1E")
        self.assertEqual(tag_response.id, 1)
        self.assertEqual(tag_response.name, "javascript")
        self.assertEqual(tag_response.color, "#F7DF1E")

    def test_tag_response_from_orm(self):
        tag = Tag(name="rust", color="#CE422B")
        tag.id = 42
        tag_response = TagResponse.model_validate(tag)
        self.assertEqual(tag_response.id, 42)
        self.assertEqual(tag_response.name, "rust")
        self.assertEqual(tag_response.color, "#CE422B")


if __name__ == "__main__":
    unittest.main()
