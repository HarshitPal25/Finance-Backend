# Finance Data Processing & Access Control Backend

A Django REST Framework backend for a finance dashboard system with role-based access control, financial records management, and analytics.

## Tech Stack

- **Python 3.10+**
- **Django 5.x** — Web framework
- **Django REST Framework** — REST API toolkit
- **SQLite** — Database (zero setup)
- **JWT (SimpleJWT)** — Token-based authentication
- **django-filter** — Filtering support
- **Vanilla HTML/CSS/JS** — Custom Frontend SPA with zero dependencies

## Quick Start

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Run Database Migrations
```bash
python3 manage.py migrate
```

### 3. Seed Sample Data (Optional)
```bash
python3 seed_data.py
```

This creates 3 users and 60 sample financial records:
| Username | Password | Role |
|----------|----------|------|
| admin | admin123456 | Admin |
| analyst | analyst123456 | Analyst |
| viewer | viewer123456 | Viewer |

### 4. Start the Application

You will need to run both the Django Backend API and the fully custom Vanilla JS Frontend. Open two terminal instances:

**Terminal 1 (Backend API):**
```bash
python3 manage.py runserver 8081
```
*Server runs at `http://127.0.0.1:8081/`*

**Terminal 2 (Frontend SPA):**
```bash
cd frontend
python3 -m http.server 8000
```
*Access the beautiful UI at `http://localhost:8000/`*

### 5. Run Tests
```bash
python3 manage.py test --verbosity=2
```

---

## API Documentation

### Authentication

| Method | Endpoint | Description | Auth Required |
|--------|----------|-------------|:---:|
| POST | `/api/auth/register/` | Register new user | ❌ |
| POST | `/api/auth/login/` | Login & get JWT tokens | ❌ |
| GET | `/api/auth/profile/` | View your profile | ✅ |
| POST | `/api/token/refresh/` | Refresh access token | ❌ |

#### Register
```bash
curl -X POST http://127.0.0.1:8000/api/auth/register/ \
  -H "Content-Type: application/json" \
  -d '{"username":"john","email":"john@example.com","password":"securepass123","role":"viewer"}'
```

#### Login
```bash
curl -X POST http://127.0.0.1:8000/api/auth/login/ \
  -H "Content-Type: application/json" \
  -d '{"username":"admin","password":"admin123456"}'
```

Response includes JWT tokens:
```json
{
  "success": true,
  "data": {
    "user": { "id": 1, "username": "admin", "role": "admin" },
    "tokens": {
      "access": "eyJ0eXAi...",
      "refresh": "eyJ0eXAi..."
    }
  }
}
```

Use the `access` token in all subsequent requests:
```
Authorization: Bearer eyJ0eXAi...
```

---

### User Management (Admin Only)

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/users/` | List all users |
| GET | `/api/users/<id>/` | Get user details |
| PUT/PATCH | `/api/users/<id>/update/` | Update user info |
| PUT | `/api/users/<id>/role/` | Change user role |
| PUT | `/api/users/<id>/status/` | Activate/deactivate user |
| DELETE | `/api/users/<id>/delete/` | Delete user |

#### Example: Change a user's role
```bash
curl -X PUT http://127.0.0.1:8000/api/users/3/role/ \
  -H "Authorization: Bearer <admin_token>" \
  -H "Content-Type: application/json" \
  -d '{"role":"analyst"}'
```

---

### Financial Records

| Method | Endpoint | Description | Access |
|--------|----------|-------------|--------|
| GET | `/api/records/` | List records (paginated) | All roles |
| POST | `/api/records/` | Create record | Admin |
| GET | `/api/records/<id>/` | Get single record | All roles |
| PUT/PATCH | `/api/records/<id>/` | Update record | Admin |
| DELETE | `/api/records/<id>/` | Soft-delete record | Admin |

#### Filtering & Search
```
GET /api/records/?transaction_type=expense
GET /api/records/?category=food
GET /api/records/?date_from=2024-01-01&date_to=2024-06-30
GET /api/records/?amount_min=1000&amount_max=5000
GET /api/records/?search=groceries
GET /api/records/?ordering=-amount
GET /api/records/?page=2&page_size=20
```

#### Create a Record
```bash
curl -X POST http://127.0.0.1:8000/api/records/ \
  -H "Authorization: Bearer <admin_token>" \
  -H "Content-Type: application/json" \
  -d '{
    "amount": "1500.00",
    "transaction_type": "expense",
    "category": "food",
    "date": "2024-03-15",
    "description": "Weekly groceries"
  }'
```

---

### Dashboard Analytics

| Method | Endpoint | Description | Access |
|--------|----------|-------------|--------|
| GET | `/api/dashboard/summary/` | Financial summary | Analyst, Admin |
| GET | `/api/dashboard/category-breakdown/` | Category-wise totals | Analyst, Admin |
| GET | `/api/dashboard/trends/` | Monthly trends | Analyst, Admin |
| GET | `/api/dashboard/recent-activity/` | Recent transactions | All roles |

#### Summary Response Example
```json
{
  "success": true,
  "data": {
    "total_income": "360000.00",
    "total_expenses": "180000.00",
    "net_balance": "180000.00",
    "total_records": 60,
    "profit_status": "profit"
  }
}
```

---

## Access Control Matrix

| Action | Viewer | Analyst | Admin |
|--------|:------:|:-------:|:-----:|
| View records | ✅ | ✅ | ✅ |
| View recent activity | ✅ | ✅ | ✅ |
| View dashboard summary | ❌ | ✅ | ✅ |
| View category breakdown | ❌ | ✅ | ✅ |
| View trends | ❌ | ✅ | ✅ |
| Create records | ❌ | ❌ | ✅ |
| Update records | ❌ | ❌ | ✅ |
| Delete records | ❌ | ❌ | ✅ |
| Manage users | ❌ | ❌ | ✅ |

---

## Project Structure

```
├── finance_backend/        # Django project settings
│   ├── settings.py         # Configuration (CORS, JWT etc)
│   └── urls.py             # Root URL routing
├── frontend/               # Custom Vanilla JS Frontend SPA
│   ├── app.js              # State management & API Fetch Logic
│   ├── index.html          # SPA structure
│   ├── styles.css          # Clean & Flat minimalist CSS
│   └── README_FRONTEND.md  # Frontend specific documentation
├── users/                  # Authentication & user management
│   ├── models.py           # Custom User model with roles
│   ├── serializers.py      # Data validation & transformation
│   ├── views.py            # Auth endpoints (register/login)
│   ├── user_views.py       # User management endpoints
│   ├── permissions.py      # Role-based permission classes
│   ├── utils.py            # Custom error handler
│   └── tests.py            # 19 tests
├── records/                # Financial records management
│   ├── models.py           # FinancialRecord model
│   ├── serializers.py      # Record validation
│   ├── views.py            # CRUD endpoints
│   ├── filters.py          # Django filters config
│   └── tests.py            # 15 tests
├── dashboard/              # Analytics & insights
│   ├── views.py            # Summary, trends, breakdown
│   └── tests.py            # 9 tests
├── seed_data.py            # Database seeding script
├── requirements.txt        # Python dependencies
├── GUIDE.md                # Guide to understanding Backend basics
├── GUIDE2_FRONTEND.md      # Guide to understanding the Frontend mapping
└── README.md               # This file
```

## Design Decisions & Assumptions

1. **SQLite** chosen for zero-setup simplicity. Easily swappable to PostgreSQL for production.
2. **Soft Delete** on financial records — data integrity matters in finance.
3. **JWT Authentication** — stateless, scalable, industry standard.
4. **Custom User Model** — extends Django's AbstractUser for role field.
5. **Consistent JSON Response Format** — all responses follow `{success, data/error}` pattern.
6. **Pre-defined Categories** — uses enum choices for data consistency. Easily extensible.
7. **Pagination** — default 10 items per page, configurable up to 100.
8. **Self-protection** — admins cannot delete/deactivate/demote themselves.

## Error Response Format
All errors follow a consistent format:
```json
{
  "success": false,
  "error": {
    "code": 400,
    "message": "Human readable error message",
    "details": { "field_name": ["specific error"] }
  }
}
```

## Testing

41 automated tests covering:
- ✅ User registration & login
- ✅ JWT token generation
- ✅ Role-based access control enforcement
- ✅ Financial records CRUD operations
- ✅ Input validation & error handling
- ✅ Dashboard analytics accuracy
- ✅ Filtering & search
- ✅ Soft delete behavior
- ✅ Self-protection guards
