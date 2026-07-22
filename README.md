# Todo API — FastAPI

A production-oriented REST API for user authentication and role-based task management. Administrators assign and manage tasks; users view and complete their own tasks. The service uses Argon2 password hashing, signed JWT bearer tokens, SQLAlchemy, Alembic migrations, optional asynchronous SMTP notifications, and validated configuration.

## Features

- User registration and JWT login
- Separate administrator and user authorization boundaries
- Admin task creation, listing, editing, assignment, and deletion
- User task listing, detail, and completion endpoints
- Email verification state and notification preferences
- Optional task assignment/completion email notifications
- Bounded pagination and validated request payloads
- SQLite for local development; PostgreSQL-compatible SQLAlchemy configuration
- Alembic database migrations
- Health endpoint, structured logging, restricted CORS, Docker image, linting, and tests

## Project structure

```text
todo_api_restructured/
├── alembic/                 # Migration environment and revisions
├── app/
│   ├── api/endpoints/       # Auth, admin, and user HTTP handlers
│   ├── core/                # Settings, passwords, and email delivery
│   ├── db/                  # Engine, sessions, and declarative base
│   ├── models/              # SQLAlchemy models
│   ├── schemas/             # Pydantic request/response models
│   └── services/            # Authentication and authorization services
├── scripts/create_admin.py  # Safe administrator provisioning command
├── tests/                   # API integration tests
├── .env.example
├── Dockerfile
├── main.py
├── pyproject.toml
├── requirements.txt
└── requirements-dev.txt
```

## Requirements

- Python 3.11 or newer (the Docker image uses Python 3.13)
- SQLite, or a PostgreSQL server and its SQLAlchemy driver

## Local setup

Run commands from `todo_api_restructured`.

```bash
python -m venv .venv
```

Activate the environment:

```bash
# Windows PowerShell
.venv\Scripts\Activate.ps1

# Linux/macOS
source .venv/bin/activate
```

Install dependencies and create local configuration:

```bash
pip install -r requirements-dev.txt
cp .env.example .env
```

On PowerShell, use `Copy-Item .env.example .env` instead of `cp` if needed. Replace `TODO_API_SECRET_KEY` with a random value of at least 32 characters. For example:

```bash
python -c "import secrets; print(secrets.token_urlsafe(48))"
```

Apply migrations, provision an administrator, and start the API:

```bash
alembic upgrade head
python -m scripts.create_admin admin@example.com
uvicorn main:app --reload
```

The server is available at `http://127.0.0.1:8000`:

- Swagger UI: `http://127.0.0.1:8000/docs`
- ReDoc: `http://127.0.0.1:8000/redoc`
- Health check: `http://127.0.0.1:8000/health`

## Configuration

Settings are loaded from `todo_api_restructured/.env` and use a `TODO_API_` prefix to avoid collisions with operating-system variables.

| Variable | Required | Default | Purpose |
| --- | --- | --- | --- |
| `TODO_API_SECRET_KEY` | Yes | — | JWT signing key; at least 32 characters |
| `TODO_API_DATABASE_URL` | No | `sqlite:///./todo.db` | SQLAlchemy database URL |
| `TODO_API_ACCESS_TOKEN_EXPIRE_MINUTES` | No | `30` | JWT lifetime |
| `TODO_API_CORS_ORIGINS` | No | `[]` | JSON list of allowed origins |
| `TODO_API_LOG_LEVEL` | No | `INFO` | Python log level |
| `TODO_API_DEBUG` | No | `false` | Enables reload when launching `python main.py` |
| `TODO_API_SMTP_SERVER` | No | `smtp.gmail.com` | SMTP hostname |
| `TODO_API_SMTP_PORT` | No | `587` | SMTP port |
| `TODO_API_SMTP_USER` | No | — | SMTP login; blank disables email |
| `TODO_API_SMTP_PASSWORD` | No | — | SMTP password |
| `TODO_API_FROM_EMAIL` | No | — | Sender address |
| `TODO_API_SMTP_USE_TLS` | No | `false` | TLS from connection start (commonly port 465) |
| `TODO_API_SMTP_START_TLS` | No | `true` | Upgrade using STARTTLS (commonly port 587) |

Do not commit `.env`. In production, inject settings through the platform's secret manager. PostgreSQL support is included; set a URL such as `postgresql+psycopg://user:password@host/database`.

## API overview

All application endpoints use the `/api` prefix. Send authenticated requests with `Authorization: Bearer <access_token>`.

| Method | Path | Access | Description |
| --- | --- | --- | --- |
| `POST` | `/api/auth/register` | Public | Register a standard user |
| `POST` | `/api/auth/login` | Public | Obtain an access token |
| `POST` | `/api/auth/verify-email` | Public | Verify an email using `email` and `token` query values |
| `POST` | `/api/admin/tasks` | Admin | Create and assign a task |
| `GET` | `/api/admin/tasks` | Admin | List all tasks (`skip`, `limit`) |
| `PUT` | `/api/admin/tasks/{task_id}` | Admin | Update a task |
| `DELETE` | `/api/admin/tasks/{task_id}` | Admin | Delete a task |
| `GET` | `/api/user/tasks` | User | List assigned tasks (`skip`, `limit`) |
| `GET` | `/api/user/tasks/{task_id}` | User | Read an assigned task |
| `PUT` | `/api/user/tasks/{task_id}/complete` | User | Mark an assigned task complete |
| `PUT` | `/api/user/notifications` | User | Enable or disable notifications |
| `POST` | `/api/user/unsubscribe` | User | Disable notifications for the caller |

Administrator roles cannot be selected during public registration. Use the interactive `scripts.create_admin` management command; it creates a new administrator or promotes an existing user and securely hashes the supplied password.

## Quality checks

```bash
ruff format --check .
ruff check .
pytest --cov=app --cov-report=term-missing
```

The current suite covers health, registration/login, privilege-escalation prevention, bearer protection, administrator assignment, user completion, and task deletion.

## Docker

Build the image from `todo_api_restructured`:

```bash
docker build -t todo-api .
docker run --rm -p 8000:8000 --env-file .env todo-api
```

Run `alembic upgrade head` as a release step before starting application replicas. For SQLite, mount a writable volume for the database file; for multi-instance production deployments, prefer PostgreSQL.

## Production checklist

- Use a unique secret from a secret manager and rotate it intentionally.
- Configure explicit HTTPS frontend origins in `TODO_API_CORS_ORIGINS`.
- Terminate TLS at a trusted reverse proxy or load balancer.
- Use PostgreSQL, connection limits appropriate to the worker count, and automated backups.
- Run exactly one migration job before rolling out new application instances.
- Configure SMTP credentials only when notifications are needed.
- Add rate limiting at the API gateway for registration and login endpoints.
- Send logs to centralized storage and monitor `/health`.
- Run the container as its included non-root `app` user.

## License

No license has been specified. Add one before distributing the project publicly.
