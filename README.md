# English LMS — Learning Management System

A full-stack English language learning platform built with **Django REST Framework** and **React**. Supports CEFR levels (A1 → C2) plus IELTS, role-based access, video lessons, vocabulary, quizzes, exercises, progress tracking, and a gamified leaderboard.

---

## Tech Stack

| Layer | Technology |
|-------|-----------|
| Backend | Django 5.2, Django REST Framework 3.16 |
| Auth | Simple JWT (7-day access / 30-day refresh) |
| Database | SQLite (development) |
| Frontend | React 19, Vite 7 |
| Styling | TailwindCSS 3 |
| HTTP Client | Axios |
| Static Files | WhiteNoise |
| AI Integration | Anthropic SDK |

---

## Project Structure

```
lrnen/
├── accounts/        # User auth & student management
├── courses/         # Lessons, vocabulary, progress
├── quiz/            # Quizzes & exercises
├── comments/        # Lesson comments
├── englishLMS/      # Django settings & root URLs
├── frontend/        # React + Vite SPA
│   └── src/
│       ├── pages/       # Login, Dashboard, Lessons, Leaderboard…
│       ├── components/  # Navbar, Exercises, Vocabulary…
│       ├── context/     # Auth & app-level state
│       └── api.js       # Axios instance with JWT injection
├── requirements.txt
└── manage.py
```

---

## Features

- **7 learning levels** — A1, A2, B1, B2, C1, C2, IELTS
- **Video lessons** with descriptions and ordering
- **Vocabulary** — English/Uzbek translations with examples
- **5 exercise types** — choose_correct, fill_blank, matching, listening, speaking
- **Multiple-choice quizzes** with automatic scoring
- **Progress tracking** — per-lesson status and score
- **XP leaderboard** — top 20 students ranked by experience points
- **Lesson comments** — per-lesson discussion thread
- **Role-based access** — Admin vs Student permissions throughout
- **Admin panel** — full CRUD for all content + student management
- **Responsive UI** — desktop Navbar + mobile MobileNav

---

## Data Model

```
User ──M2M──► Level
User ──1:M──► UserProgress
User ──1:M──► Comment

Category ──1:M──► Lesson
Level    ──M2M──► Lesson

Lesson ──1:M──► Quiz
Lesson ──1:M──► Exercise
Lesson ──1:M──► Vocabulary
Lesson ──1:M──► UserProgress
Lesson ──1:M──► Comment
```

---

## API Reference

### Auth — `/api/auth/`

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/login/` | Login → JWT tokens + user data |
| POST | `/token/refresh/` | Refresh access token |
| GET | `/me/` | Current user profile |
| PUT | `/me/` | Update profile |
| GET | `/leaderboard/` | Top 20 students by XP |
| GET/POST | `/students/` | List / create students (admin) |
| GET/PATCH/DELETE | `/students/<id>/` | Manage a student (admin) |

### Courses — `/api/courses/`

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET/POST | `/categories/` | List / create categories |
| GET/PUT/DELETE | `/categories/<id>/` | Manage category |
| GET | `/levels/` | All CEFR levels |
| GET/POST | `/lessons/` | List / create lessons |
| GET/PUT/DELETE | `/lessons/<id>/` | Manage lesson |
| GET/POST | `/vocabulary/` | List / create vocabulary |
| PUT/DELETE | `/vocabulary/<id>/` | Manage vocabulary item |
| GET/POST | `/progress/` | Get / update lesson progress |
| GET | `/stats/` | Dashboard statistics |

### Quiz & Exercises — `/api/quiz/`

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET/POST | `/` | List / create quizzes |
| GET/PUT/DELETE | `/<id>/` | Manage quiz |
| POST | `/submit/` | Submit answers → score + XP |
| GET/POST | `/exercises/` | List / create exercises |
| PUT/DELETE | `/exercises/<id>/` | Manage exercise |

### Comments — `/api/comments/`

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET/POST | `/` | List / create comments (filter by `?lesson=<id>`) |
| DELETE | `/<id>/` | Delete comment (owner or admin) |

---

## Getting Started

### Prerequisites

- Python 3.10+
- Node.js 18+

### Backend

```bash
# 1. Clone and enter the project
git clone <repo-url>
cd lrnen

# 2. Create virtual environment
python -m venv venv
source venv/bin/activate   # Windows: venv\Scripts\activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Set environment variables
cp .env.example .env
# Edit .env and set SECRET_KEY and ANTHROPIC_API_KEY

# 5. Run migrations
python manage.py migrate

# 6. Create superuser
python manage.py createsuperuser

# 7. Start development server
python manage.py runserver
```

### Frontend

```bash
cd frontend
npm install
npm run dev
```

The frontend dev server runs on `http://localhost:5173` and proxies API calls to Django on `http://localhost:8000`.

### Environment Variables

```env
SECRET_KEY=your-django-secret-key
DEBUG=True
ANTHROPIC_API_KEY=your-anthropic-api-key
```

---

## XP / Scoring System

- Completing a lesson awards **100 base XP + quiz score**
- The leaderboard ranks the **top 20 students** by total XP
- Quiz submission automatically updates `UserProgress` and recalculates the student's score

---

## Django Admin

Access the built-in admin panel at `/admin/` with a superuser account to manage all models directly.

---

## License

MIT
