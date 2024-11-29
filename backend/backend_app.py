import datetime

import limiter
from flask import Flask, jsonify, request
from flask_cors import CORS
from flask_swagger_ui import get_swaggerui_blueprint
from marshmallow import Schema, fields, ValidationError

app = Flask(__name__)
CORS(app)  # This will enable CORS for all routes

ID = "id"
TITLE = "title"
CONTENT = "content"
AUTHOR = "author"
DATE = "date"

# Sorting and Direction of Post
DIRECTION_ASC = "asc"
DIRECTION_DESC = "desc"

POSTS = [
    {"id": 1, "title": "First post", "content": "This is the first post.",
     "author": "Jerome", "date": "2023-06-07"},
    {"id": 2, "title": "Second post", "content": "This is the second post.",
     "author": "Savanna", "date": "2024-06-07"},
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
    author = fields.Str(required=True)
    date = fields.Str(required=True)


schema = ItemSchema()


@app.route('/api/posts', methods=['GET', 'POST'])
@limiter.limit("10/minute")
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

    else:
        options_directions = [DIRECTION_ASC, DIRECTION_DESC]
        options_sort = [CONTENT, TITLE, AUTHOR, DATE]

        sort = request.args.get('sort')
        direction = request.args.get('direction')

        if direction is None and sort is None:
            return jsonify(POSTS)

        if direction not in options_directions:
            return jsonify(
                standard_error_response(400,
                                        "Bad Request",
                                        "VALIDATION_ERROR_INVALID_DIRECTION",
                                        "Validation failed.",
                                        f"The direction field is invalid. [{direction}]",
                                        "/api/posts"

                                        )), 400

        if sort not in options_sort:
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
                if sort == DATE:
                    return jsonify(
                        sorted(POSTS,
                               key=lambda post: datetime.date.fromisoformat(
                                   post[sort]),
                               reverse=True))

                return jsonify(
                    sorted(POSTS, key=lambda post: post[sort], reverse=True))
            else:
                if sort == DATE:
                    return jsonify(sorted(POSTS, key=lambda
                        post: datetime.date.fromisoformat(
                        post[sort])))

                return jsonify(sorted(POSTS, key=lambda post: post[sort]))


def find_post_by_id(post_id):
    post = [post for post in POSTS if post[ID] == post_id]

    return post[0] if post else None


@app.route('/api/posts/<int:id>', methods=['DELETE'])
@limiter.limit("10/minute")
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
@limiter.limit("10/minute")
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
    post[AUTHOR] = new_data.get(AUTHOR, post[AUTHOR])
    post[DATE] = new_data.get(DATE, post[DATE])

    return jsonify(post)


@app.route('/api/posts/search', methods=['GET'])
@limiter.limit("10/minute")
def search_posts():
    title = request.args.get(TITLE)
    content = request.args.get(CONTENT)
    author = request.args.get(AUTHOR)
    date_post = request.args.get(DATE)

    if title and content:
        filtered_title_content = [post for post in POSTS if
                                  (title in post.get(TITLE))
                                  and (content in post.get(CONTENT))
                                  ]

        if filtered_title_content:
            return jsonify(filtered_title_content)

    if title and author:
        filtered_title_author = [post for post in POSTS if
                                 (title in post.get(TITLE))
                                 and (author in post.get(AUTHOR))
                                 ]

        if filtered_title_author:
            return jsonify(filtered_title_author)

    if title and date_post:
        filtered_title_date_post = [post for post in POSTS if
                                    (title in post.get(TITLE))
                                    and (date_post in post.get(DATE))
                                    ]

        if filtered_title_date_post:
            return jsonify(filtered_title_date_post)

    if title and content and author and date_post:
        filtered_title_content = [post for post in POSTS if
                                  (title in post.get(TITLE))
                                  and (content in post.get(CONTENT))
                                  and (author in post.get(AUTHOR))
                                  and (date_post in post.get(DATE))
                                  ]

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

    if author:
        filtered_author = [post for post in POSTS if
                           author in post.get(AUTHOR)]

        if filtered_author:
            return jsonify(filtered_author)

    if date_post:
        filtered_date_post = [post for post in POSTS if
                              date_post in post.get(DATE)]

        if filtered_date_post:
            return jsonify(filtered_date_post)

    return jsonify([])


SWAGGER_URL = "/api/docs"
API_URL = "/static/masterblog.json"

swagger_ui_blueprint = get_swaggerui_blueprint(
    SWAGGER_URL,
    API_URL,
    config={
        'app_name': 'Masterblog API'
    }
)
app.register_blueprint(swagger_ui_blueprint, url_prefix=SWAGGER_URL)

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5002, debug=True)
