import datetime

from flask_limiter import Limiter
from flask import Flask, jsonify, request
from flask_cors import CORS
from flask_limiter.util import get_remote_address
from flask_swagger_ui import get_swaggerui_blueprint
from marshmallow import Schema, fields, ValidationError

"""
Masterblog API

This Flask application serves as a simple blogging platform, providing CRUD
functionality for managing blog posts. It includes features such as
rate limiting, validation, sorting, and searching, along with
Swagger documentation for API reference.

Features:
- Rate Limiting: Limits API usage to prevent abuse (e.g., 10 requests per minute).
- Validation: Ensures data integrity using Marshmallow.
- Swagger Documentation: Interactive API reference accessible at `/api/docs`.
- Sorting and Filtering: Flexible query parameters for retrieving posts.
- In-memory Data: Posts are stored temporarily in memory for simplicity (not persistent).

"""

app = Flask(__name__)
limiter = Limiter(app=app, key_func=get_remote_address)
CORS(app)

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
    """
    Constructs a standardized error response dictionary.

    Parameters:
    -----------
    status : int
        The HTTP status code for the error (e.g., 400, 404, 500).
    error : str
        A brief description of the error type (e.g., "Bad Request", "Not Found").
    error_code : str
        A unique code representing the specific error (e.g., "VALIDATION_ERROR").
    message : str
        A detailed error message providing context about the error.
    details : str
        Additional information or debug details about the error.
    path : str
        The API path or endpoint where the error occurred.
    """
    return {
        "status": f"{status}",
        "error": f"{error}",
        "errorCode": f"{error_code}",
        "message": f"{message}",
        "details": f"{details}",
        "path": f"{path}"
    }


def jsonify_response(payload):
    """
    Constructs a standardized JSON response for the API.

    Parameters:
    -----------
    payload : list or dict
        The main data to include in the response, typically a list of posts
        or a single post object.
    """
    return {
        "posts": payload,
        "createdAt": datetime.datetime.now().isoformat()
    }


class ItemSchema(Schema):
    """
    Defines the schema for validating blog post data.

    Fields:
    -------
    title : fields.Str
        The title of the blog post. This field is required.
    content : fields.Str
        The content of the blog post. This field is required.
    author : fields.Str
        The author of the blog post. This field is required.
    date : fields.Str
        The date of the blog post in string format (e.g., "YYYY-MM-DD").
        This field is required.
    """
    title = fields.Str(required=True)
    content = fields.Str(required=True)
    author = fields.Str(required=True)
    date = fields.Str(required=True)


schema = ItemSchema()


@app.route('/api/v1/posts', methods=['GET', 'POST'])
@limiter.limit("10/minute")
def get_posts():
    """
    Handles requests to the '/api/v1/posts' endpoint for retrieving or creating posts.

    Methods:
    --------
    GET:
        - Retrieves a list of blog posts.
        - Supports sorting and ordering based on query parameters:
            * sort: Attribute to sort by (e.g., "content", "title", "author", "date").
            * direction: Sorting direction ("asc" or "desc").
        - If no query parameters are provided, returns the unsorted list of posts.

    POST:
        - Creates a new blog post.
        - Validates the input data using the `ItemSchema`.
        - Automatically assigns a unique ID to the new post.


    Query Parameters (GET):
    ------------------------
    sort : str, optional
        The attribute to sort the posts by (e.g., "content", "title", "author", "date").
    direction : str, optional
        The direction to sort the posts ("asc" for ascending, "desc" for descending).
    """
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
                                        "/api/v1/posts"

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
                                        "/api/v1/posts"

                                        )), 400

        if sort not in options_sort:
            return jsonify(
                standard_error_response(400,
                                        "Bad Request",
                                        "VALIDATION_ERROR_INVALID_SORT",
                                        "Validation failed.",
                                        f"The sort field is invalid. [{sort}]",
                                        "/api/v1/posts"

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
    """
    Finds a blog post by its unique ID.

    Parameters:
    -----------
    post_id : int
        The unique identifier of the post to search for.
    """
    post = [post for post in POSTS if post[ID] == post_id]

    return post[0] if post else None


@app.route('/api/v1/posts/<int:id>', methods=['DELETE'])
@limiter.limit("10/minute")
def delete_post(id):
    """
    Deletes a blog post by its unique ID.

    Parameters:
    -----------
    id : int
        The unique identifier of the post to delete.

    Returns:
    --------
    JSON Response:
        - If the post is found and successfully deleted:
          The deleted post as a JSON object.
        - If no post is found with the provided ID:
          A standardized error response with status 404.
    """
    post = find_post_by_id(id)

    if post is None:
        return jsonify(
            standard_error_response(404,
                                    "Not Found",
                                    "RESOURCE_NOT_FOUND",
                                    "The requested resource could not be found.",
                                    [
                                        f"No records match the provided ID {id}."],
                                    "/api/v1/posts"
                                    )), 404

    POSTS.remove(post)

    return jsonify(
        {"message": f"Post with id {id} has been deleted successfully."})


@app.route('/api/v1/posts/<int:id>', methods=['PUT'])
@limiter.limit("10/minute")
def handle_post(id):
    """
    Updates an existing blog post by its unique ID.

    Parameters:
    -----------
    id : int
        The unique identifier of the post to update.

    Returns:
    --------
    JSON Response:
        - If the post is found and successfully updated:
          The updated post as a JSON object.
        - If no post is found with the provided ID:
          A standardized error response with status 404.
        - If validation fails: A standardized error response with status 400.
    """
    post = find_post_by_id(id)

    if post is None:
        return jsonify(
            standard_error_response(404,
                                    "Not Found",
                                    "RESOURCE_NOT_FOUND",
                                    "The requested resource could not be found.",
                                    [
                                        f"No records match the provided ID {id}."],
                                    "/api/v1/posts"
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
                                    "/api/v1/posts"
                                    )), 400

    post[TITLE] = new_data.get(TITLE, post[TITLE])
    post[CONTENT] = new_data.get(CONTENT, post[CONTENT])
    post[AUTHOR] = new_data.get(AUTHOR, post[AUTHOR])
    post[DATE] = new_data.get(DATE, post[DATE])

    return jsonify(post)


@app.route('/api/v1/posts/search', methods=['GET'])
@limiter.limit("10/minute")
def search_posts():
    """
    Searches for blog posts based on query parameters.

    If no matching posts are found, an empty list is returned.

    Query Parameters:
    -----------------
    title : str (optional)
        The title of the post to search for.
    content : str (optional)
        The content of the post to search for.
    author : str (optional)
        The author of the post to search for.
    date : str (optional)
        The date of the post to search for.

    Returns:
    --------
    JSON Response:
        - A list of posts matching the search criteria, or an empty list if no matches are found.

    Response Codes:
    ---------------
    - 200: Successfully returned the filtered list of posts.

    """
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
