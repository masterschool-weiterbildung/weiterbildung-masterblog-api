
# Masterblog API

A RESTful blogging platform built with Flask, providing features for managing blog posts, including creating, reading, updating, deleting, sorting, and searching. The API also includes rate limiting, validation, and interactive Swagger documentation.

---

## Features

- **CRUD Operations**: Manage blog posts (Create, Read, Update, Delete).
- **Sorting and Filtering**: Retrieve posts with flexible query parameters.
- **Rate Limiting**: Prevent abuse with request limits (e.g., 10 requests per minute).
- **Validation**: Ensure data integrity using Marshmallow.
- **Swagger UI**: Interactive API documentation available at `/api/docs`.
- **Cross-Origin Support**: Enabled with Flask-CORS.

---

## Installation

1. Clone the repository:
   ```bash
   git clone git@github.com:masterschool-weiterbildung/weiterbildung-masterblog-api.git
   cd masterblog-api
   ```

2. Create and activate a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Run the application:
   ```bash
   python app.py
   ```

5. Access the API:
   - Base URL: `http://localhost:5002`
   - Swagger UI: `http://localhost:5002/api/docs`

---

## API Endpoints

### `/api/v1/posts`
- **GET**: Retrieve all posts with optional sorting (`sort`, `direction`).
- **POST**: Add a new post (requires `title`, `content`, `author`, `date`).

### `/api/v1/posts/<id>`
- **DELETE**: Remove a post by ID.
- **PUT**: Update post details by ID.

### `/api/v1/posts/search`
- **GET**: Search for posts by `title`, `content`, `author`, or `date`.

### `/api/docs`
- Swagger UI for interactive API documentation.

---

## Examples

### Adding a Post
**Request:**
```bash
curl -X POST http://localhost:5002/api/v1/posts \
-H "Content-Type: application/json" \
-d '{"title": "My Post", "content": "This is the content.", "author": "Author Name", "date": "2024-11-29"}'
```

**Response:**
```json
{
  "posts": {
    "id": 3,
    "title": "My Post",
    "content": "This is the content.",
    "author": "Author Name",
    "date": "2024-11-29"
  },
  "createdAt": "2024-11-29T12:34:56.789123"
}
```

### Searching for Posts
**Request:**
```bash
curl -X GET "http://localhost:5002/api/v1/posts/search?title=My%20Post"
```

**Response:**
```json
[
  {
    "id": 3,
    "title": "My Post",
    "content": "This is the content.",
    "author": "Author Name",
    "date": "2024-11-29"
  }
]
```

### Dependencies
Install the required Python packages using:
```bash
pip install -r requirements.txt
```

- **Flask**: Web framework for the API.
- **Flask-Limiter**: Rate limiting for API endpoints.
- **Flask-CORS**: Cross-Origin Resource Sharing support.
- **Flask-Swagger-UI**: Swagger integration for API documentation.
- **Marshmallow**: Schema-based validation.
- **Datetime**: Handling date and time.

---

## Notes

- Data is stored in memory and will reset when the server restarts.
- Errors are returned in a consistent format with status, error code, and details.
