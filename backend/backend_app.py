import datetime

from flask import Flask, jsonify, request
from flask_cors import CORS
from marshmallow import Schema, fields, ValidationError

app = Flask(__name__)
CORS(app)  # This will enable CORS for all routes

ID = "id"
TITLE = "title"
CONTENT = "content"

# Sorting and Direction of Post
DIRECTION_ASC = "asc"
DIRECTION_DESC = "desc"

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

    sort = request.args.get('sort')
    direction = request.args.get('direction')

    if direction is None and sort is None:
        return jsonify(POSTS)

    if direction != DIRECTION_ASC and direction != DIRECTION_DESC:
        return jsonify(
            standard_error_response(400,
                                    "Bad Request",
                                    "VALIDATION_ERROR_INVALID_SORT_DIRECTION",
                                    "Validation failed.",
                                    f"The direction field is invalid. [{direction}]",
                                    "/api/posts"

                                    )), 400

    if sort != TITLE and sort != CONTENT:
        return jsonify(
            standard_error_response(400,
                                    "Bad Request",
                                    "VALIDATION_ERROR_INVALID_SORT",
                                    "Validation failed.",
                                    f"The sort field is invalid. [{sort}]",
                                    "/api/posts"

                                    )), 400

    if sort and direction:
        if direction == "desc":
            return jsonify(
                sorted(POSTS, key=lambda post: post[sort], reverse=True))
        else:
            return jsonify(sorted(POSTS, key=lambda post: post[sort]))


def find_post_by_id(post_id):
    post = [post for post in POSTS if post[ID] == post_id]

    return post[0] if post else None


@app.route('/api/posts/<int:id>', methods=['DELETE'])
def delete_post(id):
    post = find_post_by_id(id)

    if post is None:
        return jsonify(
            standard_error_response(404,
                                    "Not Found",
                                    "RESOURCE_NOT_FOUND",
                                    "The requested resource could not be found.",
                                    [
                                        f"No records match the provided ID {id}."],
                                    "/api/posts"
                                    )), 404

    POSTS.remove(post)

    return jsonify(post)


@app.route('/api/posts/<int:id>', methods=['PUT'])
def handle_post(id):
    post = find_post_by_id(id)

    if post is None:
        return jsonify(
            standard_error_response(404,
                                    "Not Found",
                                    "RESOURCE_NOT_FOUND",
                                    "The requested resource could not be found.",
                                    [
                                        f"No records match the provided ID {id}."],
                                    "/api/posts"
                                    )), 404

    try:
        new_data = schema.load(request.get_json())
    except ValidationError as err:
        return jsonify(
            standard_error_response(400,
                                    "Bad Request",
                                    "VALIDATION_ERROR_MISSING_TITLE_CONTENT",
                                    "Validation failed.",
                                    f"{err}",
                                    "/api/posts"
                                    )), 400

    post[TITLE] = new_data.get(TITLE, post[TITLE])
    post[CONTENT] = new_data.get(CONTENT, post[CONTENT])

    return jsonify(post)


@app.route('/api/posts/search', methods=['GET'])
def search_posts():
    title = request.args.get(TITLE)
    content = request.args.get(CONTENT)

    if title and content:
        filtered_title_content = [post for post in POSTS if
                                  (title in post.get(TITLE)) and (
                                          content in post.get(CONTENT))]

        if filtered_title_content:
            return jsonify(filtered_title_content)

    if title:
        filtered_title = [post for post in POSTS if
                          title in post.get(TITLE)]

        if filtered_title:
            return jsonify(filtered_title)

    if content:
        filtered_content = [post for post in POSTS if
                            content in post.get(CONTENT)]

        if filtered_content:
            return jsonify(filtered_content)

    return jsonify([])


if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5002, debug=True)
