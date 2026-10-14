# User Management – Clean Code App

A user management app built by re-architecting a Go (GoFiber) Clean Architecture template into **Python FastAPI**, keeping the
original business logic, plus a **React** frontend that consumes the API.

- `python-api/`: FastAPI backend (the main app)
- `frontend/`: React + Tailwind web app
- `src/`: original Go app, kept as reference

## Features

- Register
- Login and logout (JWT with automatic token refresh)
- View profile
- View users list with search, pagination and page size
- View user details
- API docs with Swagger

## Tech Stack

| Layer | Technology |
|---|---|
| Frontend | React, TypeScript, Vite, Tailwind CSS |
| Backend | Python, FastAPI, SQLAlchemy, Alembic |
| Database | PostgreSQL |
| Docker | Docker Compose (runs PostgreSQL) |

## Project Structure

```
python-api/
├── app/
│   ├── api/            # API routes and request auth
│   ├── usecases/       # business logic
│   ├── domain/         # schemas, interfaces, errors
│   ├── repositories/   # database queries
│   ├── models/         # database tables
│   └── core/           # config, database, security, errors
├── alembic/            # database migrations
└── tests/              # unit and API tests

frontend/src/
├── api/                # API calls
├── auth/               # login state and protected routes
├── components/         # shared UI components
├── hooks/              # shared React hooks
└── pages/              # app pages
```

## How to Run

**Requirements:** Docker, Python 3.12+ (developed and tested on 3.14), Node.js 22.22+

### 1. Database (Docker)

```bash
docker compose up -d db
```

This starts PostgreSQL on `localhost:5432` (user `postgres`, password `golang-first-api`).

### 2. Backend (FastAPI)

```bash
cd python-api
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements-dev.txt

cp .env.example .env         
alembic upgrade head          # create tables + seed the test user
python -m app.main            # http://127.0.0.1:3000
```

- API docs: http://127.0.0.1:3000/docs
- Test user: `user@example.com` / `123456`
- Run tests: `pytest`

### 3. Frontend (React)

In a second terminal (the backend must be running):

```bash
cd frontend
npm install
npm run dev                   # http://localhost:5173
```

## Screenshots

<!-- Add images to docs/screenshots/ and uncomment the lines below -->

- Register
<img width="1447" height="802" alt="Screenshot 2569-10-14 at 17 32 18" src="https://github.com/user-attachments/assets/a4a3b57e-d217-4e58-96ed-92a6982ef5b0" />

- User view
<img width="1450" height="595" alt="Screenshot 2569-10-14 at 17 32 04" src="https://github.com/user-attachments/assets/3d3813d2-40aa-4c34-b837-f1c981710456" />

