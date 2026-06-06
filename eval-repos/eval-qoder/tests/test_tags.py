import unittest
from pydantic import ValidationError
from app.schemas.tags import TagCreate, TagResponse


class TestTagCreate(unittest.TestCase):
    def test_valid_tag_create(self):
        tag = TagCreate(name="python", color="#3776AB")
        self.assertEqual(tag.name, "python")
        self.assertEqual(tag.color, "#3776AB")

    def test_empty_name_rejected(self):
        with self.assertRaises(ValidationError):
            TagCreate(name="", color="#000000")

    def test_name_too_long_rejected(self):
        with self.assertRaises(ValidationError):
            TagCreate(name="x" * 51, color="#000000")

    def test_invalid_color_no_hash_rejected(self):
        with self.assertRaises(ValidationError):
            TagCreate(name="tag", color="000000")

    def test_invalid_color_short_rejected(self):
        with self.assertRaises(ValidationError):
            TagCreate(name="tag", color="#FFF")

    def test_invalid_color_non_hex_rejected(self):
        with self.assertRaises(ValidationError):
            TagCreate(name="tag", color="#GGGGGG")

    def test_missing_fields_rejected(self):
        with self.assertRaises(ValidationError):
            TagCreate()


class TestTagResponse(unittest.TestCase):
    def test_tag_response(self):
        tag = TagResponse(id=1, name="python", color="#3776AB")
        self.assertEqual(tag.id, 1)
        self.assertEqual(tag.name, "python")
        self.assertEqual(tag.color, "#3776AB")

    def test_tag_response_from_attributes(self):
        class FakeORM:
            id = 1
            name = "fastapi"
            color = "#009688"
        tag = TagResponse.model_validate(FakeORM(), from_attributes=True)
        self.assertEqual(tag.name, "fastapi")


if __name__ == "__main__":
    unittest.main()
