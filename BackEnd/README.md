# FastAPI Blog Backend (Stage 1 Completed)

## 📝 Overview
This is the **backend for a production-grade blog platform** built using FastAPI and SQLite.  


## 🚀 Features Implemented (Stage 1)
| Feature        | Status | Description                                    |
| -------------- | ------ | ---------------------------------------------- |
| User CRUD      | ✅     | Create, read, update, delete users             |
| Post CRUD      | ✅     | Create, read, update, delete blog posts       |
| Modular Code   | ✅     | Folder structure for routes, models, schemas  |
| Database Setup | ✅     | SQLite database with SQLAlchemy ORM           |


## 📂 Current Folder Structure 
backend/
├── app/
│ ├── main.py # FastAPI entry point
│ ├── databaseSetup.py # SQLite connection setup
│ ├── model.py # SQLAlchemy ORM models
│ ├── schemas.py # Pydantic validation models
│ ├── routes/
│ │ ├── posts_routes
│ │ ├── user_routes.py
│ │ └── comments_routes.py
├── requirements.txt
└── README.md


## ⚙️ Setup Instructions
1. Create & activate virtual environment
    python -m venv myenv
    myenv\Scripts\activate      # Windows

2. Install dependencies
    python -m pip install --upgrade pip
    python -m pip install -r requirements.txt

3. Run the backend server
    python -m uvicorn app.main:app --reload

4. Access API docs
    http://127.0.0.1:8000/docs


## 🔧API Endpoints
..............................................................................
Endpoint                       | Method   | Auth Required | Description
................................|.........|..............|.................................
/api/v1/register                | POST    | ❌            | Register a new user
/api/v1/login                   | POST    | ✅            | Login
/api/v1/posts/                  | GET     | ❌            | List all posts
/api/v1/posts/{id}              | GET     | ❌            | Retrieve post details
/api/v1/posts/                  | POST    | ✅            | Create a new post
/api/v1/posts/{id}              | PUT     | ✅            | Update a post
/api/v1/posts/{id}              | DELETE  | ✅            | Delete a post
/api/v1/posts/{id}/comments/    | GET     | ❌            | List comments for a post
/api/v1/posts/{id}/comments/    | POST    | ✅            | Add a comment to a post
/api/v1/comments/{id}           | PUT     | ✅            | Update a comment
/api/v1/comments/{id}           | DELETE  | ✅            | Delete a comment
..............................................................................

