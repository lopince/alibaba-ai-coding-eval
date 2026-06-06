from marshmallow import Schema, fields, validate


class UserCreateSchema(Schema):
    username = fields.String(required=True, validate=validate.Length(min=3, max=50))
    email = fields.Email(required=True)
    full_name = fields.String(validate=validate.Length(max=100))
    password = fields.String(required=True, validate=validate.Length(min=8))


class UserResponseSchema(Schema):
    id = fields.Integer()
    username = fields.String()
    email = fields.String()
    full_name = fields.String()
    is_active = fields.Boolean()


class UserUpdateSchema(Schema):
    email = fields.Email(required=True)


class PostCreateSchema(Schema):
    title = fields.String(required=True, validate=validate.Length(min=1, max=200))
    body = fields.String(validate=validate.Length(max=5000))


class PostResponseSchema(Schema):
    id = fields.Integer()
    title = fields.String()
    body = fields.String()
    author_id = fields.Integer()


class CommentCreateSchema(Schema):
    post_id = fields.Integer(required=True)
    content = fields.String(required=True, validate=validate.Length(min=1, max=1000))


class CommentResponseSchema(Schema):
    id = fields.Integer()
    post_id = fields.Integer()
    author_id = fields.Integer()
    content = fields.String()
    created_at = fields.String()
