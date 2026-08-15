# Smart Campus Issue Reporting System

A full-stack web application for reporting and managing campus issues. Students can submit issues with images, and admins can track and update their status.

## Tech Stack

- **Frontend:** HTML, Tailwind CSS, Vanilla JavaScript
- **Backend:** Python Flask
- **Database:** SQLite with SQLAlchemy ORM

## Features

### Student
- Sign up and log in
- Dashboard with quick "Report Issue" action
- Submit issues with title, description, category, and optional image
- View "My Issues" with status badges (Pending, In Progress, Resolved)

### Admin
- Admin login (separate from student)
- Dashboard with analytics (total, pending, in progress, resolved)
- Table + card hybrid view of all issues
- Filter by category and status
- Update issue status (Pending → In Progress → Resolved)

## Setup & Run

### 1. Create a virtual environment (recommended)

```bash
python -m venv venv
venv\Scripts\activate
```

### 2. Install dependencies

```bash
pip install -r requirements.txt
```

### 3. Run the application

```bash
python run.py
```

The app will be available at **http://127.0.0.1:5000**

### Default Admin Credentials

- **Email:** admin@campus.edu  
- **Password:** admin123  

*Change these in production!*

## Project Structure

```
├── app.py              # Flask application & API routes
├── config.py           # Configuration
├── extensions.py       # Flask extensions (SQLAlchemy)
├── models.py           # User & Issue models
├── run.py              # Entry point
├── requirements.txt
├── templates/          # HTML templates
├── uploads/            # Uploaded issue images
└── README.md
```

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/auth/signup` | Student registration |
| POST | `/api/auth/login` | Student login |
| POST | `/api/auth/admin/login` | Admin login |
| POST | `/api/auth/logout` | Logout |
| GET | `/api/auth/me` | Current user info |
| GET | `/api/issues` | List issues (with optional `?category=` & `?status=`) |
| POST | `/api/issues` | Create issue (multipart form) |
| PATCH | `/api/issues/<id>/status` | Update issue status |
| GET | `/api/issues/stats` | Admin analytics |

## License

MIT

link for the app: https://smart-campus-issues.onrender.com/login
