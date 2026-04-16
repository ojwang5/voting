# VOTING HUB Voting System

A secure, multi-user voting system built with Django 5.1. Features user authentication, poll creation, voting, real-time results, API endpoints, and comprehensive security.

## Features
- ✅ User registration/login/logout
- ✅ One vote per user per poll
- ✅ Admin poll management (create/edit/delete/close)
- ✅ Real-time results with progress bars
- ✅ REST API for polls and voting
- ✅ CSRF/XSS protection
- ✅ Unit tests
- ✅ Responsive Bootstrap frontend
- ✅ Race condition prevention

## Quick Start

1. **Create virtual environment & install dependencies:**
   ```bash
   cd C:/Users/user/Desktop/voting_system
   python -m venv venv
   venv\Scripts\activate
   pip install -r requirements.txt
   ```

2. **Run migrations & create superuser:**
   ```bash
   python manage.py makemigrations
   python manage.py migrate
   python manage.py createsuperuser
   ```

3. **Start development server:**
   ```bash
   python manage.py runserver
   ```

4. **Access the app:**
   - Homepage: http://127.0.0.1:8000/polls/
   - Admin: http://127.0.0.1:8000/admin/
   - API: http://127.0.0.1:8000/polls/api/polls/

## Architecture
```
voting_system/
├── manage.py
├── voting_system/         # Project settings
├── polls/                 # Main app
│   ├── models.py         # Poll, Choice, Vote
│   ├── views.py          # Web views
│   ├── views_api.py      # REST API
│   ├── forms.py          # Forms
│   ├── serializers.py    # DRF serializers
│   ├── templates/        # HTML templates
│   └── tests.py          # Unit tests
└── README.md
```

## Usage
1. Login/register at `/accounts/login/`
2. Admins create polls via "Create Poll" button or admin panel
3. Users vote on active polls (one vote per poll)
4. View results immediately after voting
5. API endpoints available for integration

## API Endpoints
- `GET /polls/api/polls/` - Active polls
- `POST /polls/api/vote/` - Cast vote (requires auth)
  ```json
  {
    "poll_id": 1,
    "choice_id": 1
  }
  ```

## Security Features
- Django CSRF & XSS protection
- Unique vote constraint (user + poll)
- Poll activation based on close_date
- Login required for voting
- Staff-only poll creation

## Testing
```bash
python manage.py test polls
```

## Key Decisions
- **SQLite** for simplicity (easy setup)
- **Django REST Framework** for clean API
- **Bootstrap 5** for responsive design
- **Atomic transactions** via model constraints
- **Class-based views** for standard CRUD

Enjoy your voting system! 🚀

