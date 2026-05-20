# KanMind Backend API

A Kanban-style project management backend built with Django and Django REST Framework. Provides RESTful endpoints for boards, tasks, and comments with token-based authentication.

## Tech Stack

- Python 3.12
- Django 6.0.5
- Django REST Framework 3.17
- python-dotenv (for environment variables)
- SQLite (development)

## Setup

### 1. Clone the repository

```bash
git clone <repository-url>
cd kanmind
```

### 2. Create and activate a virtual environment

**Windows (PowerShell):**
```bash
python -m venv env
.\env\Scripts\activate
```

**macOS/Linux:**
```bash
python -m venv env
source env/bin/activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Create your `.env` file

This project loads sensitive configuration (e.g., `SECRET_KEY`) from a `.env` file in the project root. A template is provided as `.env.example`.

Copy the template:

**Windows (PowerShell):**

```bash
copy .env.example .env
```

**macOS/Linux:**

```bash
cp .env.example .env
```

Then open `.env` and replace the placeholder `SECRET_KEY` with a real value. You can generate a new Django secret key with:

```bash
python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
```

> ⚠️ Never commit the `.env` file — it is already excluded via `.gitignore`.


### 5. Run database migrations

```bash
python manage.py migrate
```

### 6. Create a superuser

```bash
python manage.py createsuperuser
```

You will be prompted for an email and password.

### 7. Start the development server

```bash
python manage.py runserver
```

The API will be available at `http://127.0.0.1:8000/`.

## Authentication

All endpoints except `/api/registration/` and `/api/login/` require token authentication.

After registering or logging in, include the token in the `Authorization` header of subsequent requests:

```
Authorization: Token <your-token>
```

## API Endpoints

### Authentication

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/registration/` | Register a new user |
| POST | `/api/login/` | Log in and receive a token |
| GET | `/api/email-check/?email=<email>` | Check if an email is registered |

### Boards

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/boards/` | List accessible boards |
| POST | `/api/boards/` | Create a new board |
| GET | `/api/boards/<id>/` | Get board details |
| PATCH | `/api/boards/<id>/` | Update a board |
| DELETE | `/api/boards/<id>/` | Delete a board |

### Tasks

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/tasks/assigned-to-me/` | Tasks assigned to current user |
| GET | `/api/tasks/reviewing/` | Tasks where current user is reviewer |
| POST | `/api/tasks/` | Create a new task |
| PATCH | `/api/tasks/<id>/` | Update a task |
| DELETE | `/api/tasks/<id>/` | Delete a task |

### Comments

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/tasks/<task_id>/comments/` | List comments of a task |
| POST | `/api/tasks/<task_id>/comments/` | Create a new comment |
| DELETE | `/api/tasks/<task_id>/comments/<id>/` | Delete a comment |

## Testing

This API can be tested using [Postman](https://www.postman.com/) or any similar HTTP client.

Example workflow:
1. Register a user via `POST /api/registration/`
2. Use the returned token in the `Authorization` header
3. Create a board via `POST /api/boards/`
4. Create tasks, assign users, and add comments

## Admin Panel

A Django admin panel is available at `http://127.0.0.1:8000/admin/`. Use the superuser credentials created during setup to log in.


## Project Structure
```
core/                # Project settings and main URL routing
auth_app/            # User authentication
  ├── api/           # Serializers, views, urls, permissions
  └── models.py      # Custom User model
kanban_app/          # Boards, tasks, comments
  ├── api/           # Serializers, views, urls, permissions
  └── models.py      # Board, Task, Comment models
manage.py            # Django management script
requirements.txt     # Python dependencies
.env                 # Environment variables (not committed)
.gitignore           # Files excluded from Git
```