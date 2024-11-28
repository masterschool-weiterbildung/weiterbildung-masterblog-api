import datetime

from flask import Flask, jsonify, request
from flask_cors import CORS
from marshmallow import Schema, fields, ValidationError

app = Flask(__name__)
CORS(app)  # This will enable CORS for all routes
ID = "id"

POSTS = [
    {"id": 1, "title": "First post", "content": "This is the first post."},
    {"id": 2, "title": "Second post", "content": "This is the second post."},
]


def standard_error_response(status, error, error_code, message, details,
                            path):
    return {
        "status": f"{status}",
        "error": f"{error}",
        "errorCode": f"{error_code}",
        "message": f"{message}",
        "details": f"{details}",
        "path": f"{path}"
    }


def jsonify_response(payload):
    return {
        "posts": payload,
        "createdAt": datetime.datetime.now().isoformat()
    }


class ItemSchema(Schema):
    title = fields.Str(required=True)
    content = fields.Str(required=True)


schema = ItemSchema()


@app.route('/api/posts', methods=['GET', 'POST'])
def get_posts():
    if request.method == 'POST':
        try:
            new_post = schema.load(request.get_json())

            new_id = max(post['id'] for post in POSTS) + 1
            new_post['id'] = new_id

            POSTS.append(new_post)

            return jsonify(jsonify_response(new_post)), 201
        except ValidationError as err:
            return jsonify(
                standard_error_response(400,
                                        "Bad Request",
                                        "VALIDATION_ERROR_MISSING_TITLE_CONTENT",
                                        "Validation failed.",
                                        f"{err}",
                                        "/api/posts"

                                        )), 400

    return jsonify(POSTS)


def find_post_by_id(post_id):
    post = [post for post in POSTS if post[ID] == post_id]

    return post[0] if post else None


@app.route('/api/posts/<int:id>', methods=['DELETE'])
def delete_book(id):
    post = find_post_by_id(id)

    if post is None:
        return jsonify(
            standard_error_response(404,
                                    "Not Found",
                                    "RESOURCE_NOT_FOUND",
                                    "The requested resource could not be found.",
                                    [
                                        f"No records match the provided ID {id}."],
                                    "/api/v1/books"
                                    )), 404

    POSTS.remove(post)

    return jsonify(post)


if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5002, debug=True)
