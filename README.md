# Do Api
Do API is a Task/To do API that create to be a simple RESTful backend for managing to‑do tasks, built with **FastAPI** and **SQLAlchemy**.  
Users can register, log in, and then securely create and manage their own tasks via JWT-based authentication.

## Features
- User registration with unique username and email
- Secure password hashing using Argon2 (via `passlib`)
- JWT authentication with bearer tokens
- Per‑user task ownership (each task belongs to a specific user)
- CRUD-style task endpoints (create and read implemented, update/delete scaffolded)
- Task fields: title, description, completed, due date, priority
- SQLite database via SQLAlchemy ORM
- CORS enabled for frontend integration
- Static file mounting for serving a simple frontend

## Tech Stack
- **Backend:** FastAPI
- **Database:** SQLite (SQLAlchemy ORM)
- **Auth:** JWT (`python-jose`), Argon2 (`passlib`)
- **Server:** Uvicorn (recommended)

## Usage and Installation 
- Clone the repository and move into the project folder.

- Create and activate a virtual environment (optional but recommended):

   ```bash
   python -m venv venv
   source venv/bin/activate      # macOS / Linux
- Install dependencies from requirements.txt
  ```bash
  pip install -r requirements.txt

- Set environment variable
  ```bash
  export SECRET_KEY="your-strong-secret-key"

- Run Application
  ```
  uvicorn main:app reload
  ```
  or
  ```
  pip install "fastapi[standard]"
  fastapi dev
  ```
