# 📚 Complete Backend Development Guide

**A beginner-friendly guide explaining everything in this project — what happens, why it happens, and how it works.**

---

## Table of Contents
1. [What is a Backend?](#1-what-is-a-backend)
2. [How the Internet Works (Simplified)](#2-how-the-internet-works-simplified)
3. [What is Django?](#3-what-is-django)
4. [Project Architecture](#4-project-architecture)
5. [How a Request Flows Through Django](#5-how-a-request-flows-through-django)
6. [Database & Models (Where Data Lives)](#6-database--models-where-data-lives)
7. [Serializers (Data Translators)](#7-serializers-data-translators)
8. [Views (Request Handlers)](#8-views-request-handlers)
9. [URL Routing (The Address System)](#9-url-routing-the-address-system)
10. [Authentication (Who Are You?)](#10-authentication-who-are-you)
11. [Authorization & Permissions (What Can You Do?)](#11-authorization--permissions-what-can-you-do)
12. [Validation & Error Handling](#12-validation--error-handling)
13. [Dashboard Analytics (Aggregation Queries)](#13-dashboard-analytics-aggregation-queries)
14. [Testing (Proving It Works)](#14-testing-proving-it-works)
15. [Key Concepts Summary](#15-key-concepts-summary)
16. [How to Run & Test Everything](#16-how-to-run--test-everything)

---

## 1. What is a Backend?

Think of a restaurant:
- **Frontend** = The dining area (what customers see — menus, tables, decor)
- **Backend** = The kitchen (where food is prepared, stored, and managed)
- **Database** = The pantry/storage (where ingredients are kept)
- **API** = The waiter (takes orders from customers, delivers food from kitchen)

The **backend** is the part of a web application that:
- Stores and manages data
- Processes business logic (calculations, rules)
- Controls who can access what (security)
- Responds to requests from frontend applications

**Example**: When you log into Instagram:
1. The app (frontend) sends your username and password to Instagram's backend
2. The backend checks if your credentials are correct (queries the database)
3. If yes, it sends back a "token" (like a VIP wristband) that proves you're logged in
4. Every future request includes this token, so the backend knows who you are

---

## 2. How the Internet Works (Simplified)

### HTTP Requests & Responses

All communication on the web uses **HTTP (HyperText Transfer Protocol)**. It's like a conversation:

```
[Your Browser/App]  ──── HTTP Request ────>  [Server/Backend]
                    <── HTTP Response ────  
```

### HTTP Methods (Verbs)

| Method | What it does | Restaurant analogy |
|--------|-------------|-------------------|
| **GET** | Retrieve data | "Can I see the menu?" |
| **POST** | Create new data | "I'd like to order this dish" |
| **PUT** | Update data (full) | "Change my entire order to this" |
| **PATCH** | Update data (partial) | "Add extra cheese to my order" |
| **DELETE** | Remove data | "Cancel my order" |

### HTTP Status Codes

The server always responds with a **status code** (a number) that tells you what happened:

| Code | Meaning | When it's used |
|------|---------|---------------|
| **200** | OK | Request succeeded |
| **201** | Created | New resource was created |
| **400** | Bad Request | Your input was invalid |
| **401** | Unauthorized | You're not logged in |
| **403** | Forbidden | You're logged in but don't have permission |
| **404** | Not Found | The requested thing doesn't exist |
| **500** | Internal Server Error | Something broke on the server |

### JSON (JavaScript Object Notation)

Data is sent back and forth as **JSON** — a text format that looks like this:

```json
{
  "name": "Mohan",
  "age": 22,
  "skills": ["Python", "Django"],
  "is_student": true
}
```

It's essentially a dictionary/object format that both humans and computers can read easily.

---

## 3. What is Django?

**Django** is a Python web framework — a pre-built toolkit that handles the boring, repetitive parts of web development so you can focus on your application's unique logic.

### What Django gives you for free:
- 🔐 User authentication (login/logout/passwords)
- 🗄️ Database management (ORM — talk to databases with Python, not SQL)
- 🛣️ URL routing (matching URLs to your code)
- 🛡️ Security features (CSRF protection, XSS prevention, etc.)
- 👤 Admin panel (auto-generated admin interface)
- 📝 Form/data validation

### Django REST Framework (DRF)

Django itself is built for serving HTML pages. But we're building an **API** (we just send JSON data, not web pages). **Django REST Framework** extends Django to make building APIs easy.

DRF adds:
- **Serializers** — convert Python objects ↔ JSON
- **API views** — handle HTTP requests and return JSON responses
- **Authentication** — JWT tokens, session auth, etc.
- **Permissions** — control who can do what
- **Filtering & Pagination** — for listing data

---

## 4. Project Architecture

### Why separate into apps?

Django projects are organized into **apps** — self-contained modules that each handle one area of functionality:

```
finance_backend/     ← The Django "project" (configuration)
├── users/           ← App #1: Everything about users & authentication
├── records/         ← App #2: Everything about financial records
└── dashboard/       ← App #3: Everything about analytics
```

**Why?** Because:
1. **Separation of concerns** — each app handles one thing well
2. **Reusability** — you could use the `users` app in a different project
3. **Maintainability** — easier to find and fix bugs
4. **Collaboration** — different developers can work on different apps

### Files in each app

```
users/
├── models.py       ← Database tables (data structure)
├── serializers.py  ← Data validation & JSON conversion
├── views.py        ← Request handlers (the actual logic)
├── urls.py         ← URL patterns → which view handles which URL
├── permissions.py  ← Access control rules
├── utils.py        ← Helper functions
└── tests.py        ← Automated tests
```

### How they fit together (The layered architecture):

```
Request comes in
    ↓
┌─────────────┐
│   URLs      │  ← "Which view should handle this request?"
└─────┬───────┘
      ↓
┌─────────────┐
│   Views     │  ← "Process the request, apply business logic"
└─────┬───────┘
      ↓
┌─────────────┐
│ Serializers │  ← "Validate input / Format output"
└─────┬───────┘
      ↓
┌─────────────┐
│   Models    │  ← "Read/Write data to database"
└─────┬───────┘
      ↓
┌─────────────┐
│  Database   │  ← "Store data permanently"
└─────────────┘
```

---

## 5. How a Request Flows Through Django

Let's trace what happens when someone creates a financial record:

```
POST /api/records/
Authorization: Bearer eyJ0eXAi...
Content-Type: application/json

{
    "amount": "1500.00",
    "transaction_type": "expense",
    "category": "food",
    "date": "2024-03-15",
    "description": "Weekly groceries"
}
```

### Step 1: URL Matching
```
finance_backend/urls.py sees:
  /api/records/ → includes records.urls

records/urls.py sees:
  '' (empty path) → record_list_create view
```

### Step 2: Middleware & Authentication
Before the view runs:
1. Django's middleware processes the request
2. JWT authentication reads the `Authorization: Bearer ...` header
3. It decodes the token to identify the user
4. If invalid → immediately returns 401 Unauthorized

### Step 3: Permission Check
```python
@permission_classes([IsActiveUser, ReadOnlyForViewers])
```
- `IsActiveUser`: Is this user's account active?
- `ReadOnlyForViewers`: This is a POST request, so viewers are blocked (403).
  Only admins can proceed.

### Step 4: View Logic
```python
if request.method == 'POST':
    serializer = FinancialRecordSerializer(data=request.data, context={'request': request})
    if serializer.is_valid():
        serializer.save()  # Saves to database
        return Response({...}, status=201)
    return Response({...}, status=400)
```

### Step 5: Serializer Validation
The serializer checks:
- ✅ Is `amount` a positive number?
- ✅ Is `transaction_type` either "income" or "expense"?
- ✅ Is `category` one of the valid choices?
- ✅ Is `date` a valid date and not too far in the future?

If any check fails → returns detailed error messages.

### Step 6: Database Save
```python
serializer.save()
```
This creates a SQL statement like:
```sql
INSERT INTO records_financialrecord 
  (amount, transaction_type, category, date, description, created_by_id, ...)
VALUES 
  (1500.00, 'expense', 'food', '2024-03-15', 'Weekly groceries', 1, ...)
```
Django's ORM writes this SQL for you — you never write SQL manually.

### Step 7: Response
The view returns a JSON response with status 201 (Created):
```json
{
    "success": true,
    "message": "Financial record created successfully.",
    "data": {
        "id": 61,
        "amount": "1500.00",
        "transaction_type": "expense",
        ...
    }
}
```

---

## 6. Database & Models (Where Data Lives)

### What is a Model?

A **model** is a Python class that defines the structure of a database table. Each attribute becomes a column in the table.

### Our User Model (users/models.py)

```python
class User(AbstractUser):
    class Role(models.TextChoices):
        VIEWER = 'viewer', 'Viewer'
        ANALYST = 'analyst', 'Analyst'
        ADMIN = 'admin', 'Admin'
    
    email = models.EmailField(unique=True)
    role = models.CharField(max_length=10, choices=Role.choices, default=Role.VIEWER)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
```

**What this creates in the database:**

| Column | Type | Explanation |
|--------|------|-------------|
| id | INTEGER (auto) | Unique identifier, auto-generated |
| username | VARCHAR(150) | Inherited from AbstractUser |
| email | VARCHAR(254) | Must be unique |
| password | VARCHAR(128) | Stored as a HASH (not plain text!) |
| role | VARCHAR(10) | One of: viewer, analyst, admin |
| is_active | BOOLEAN | True/False |
| created_at | DATETIME | Set automatically when created |
| updated_at | DATETIME | Updated automatically on every save |

**Why `AbstractUser`?** Django has a built-in user system with login, password hashing, etc. `AbstractUser` gives us ALL of that functionality, and we just add our extra fields (role, timestamps).

### Our Financial Record Model (records/models.py)

```python
class FinancialRecord(models.Model):
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    transaction_type = models.CharField(max_length=10, choices=TransactionType.choices)
    category = models.CharField(max_length=20, choices=Category.choices)
    date = models.DateField()
    description = models.TextField(blank=True, default='')
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='financial_records')
    is_deleted = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
```

**Key concepts:**

1. **DecimalField** → Used for money because `FloatField` has floating-point precision issues (e.g., `0.1 + 0.2 = 0.30000000000000004`)

2. **ForeignKey** → Creates a relationship between tables. Each record "belongs to" a user. `on_delete=models.CASCADE` means: if the user is deleted, their records are also deleted.

3. **TextChoices** → Enum-like classes that restrict a field to specific values. Prevents invalid data like `transaction_type="invalid"`.

4. **Indexes** → We create database indexes on frequently-searched columns (type, category, date) to make queries faster.

### Migrations — How Models Become Database Tables

When you change a model, Django doesn't automatically update the database. You need to:

```bash
# Step 1: Generate migration files (Django detects what changed)
python3 manage.py makemigrations

# Step 2: Apply migrations (execute the SQL to update the database)
python3 manage.py migrate
```

**Migrations** are version-controlled files that track database changes. They're like "git commits" for your database schema.

---

## 7. Serializers (Data Translators)

### What Problem Do Serializers Solve?

- **Incoming data**: JSON string → needs to be validated → converted to Python objects → saved to database
- **Outgoing data**: Database objects → converted to Python dict → rendered as JSON string

Serializers handle BOTH directions.

### Example: UserRegistrationSerializer

```python
class UserRegistrationSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, min_length=8)
    role = serializers.ChoiceField(choices=User.Role.choices, default=User.Role.VIEWER)
    
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'password', 'role', 'created_at']
        read_only_fields = ['id', 'created_at']
    
    def validate_email(self, value):
        if User.objects.filter(email__iexact=value).exists():
            raise serializers.ValidationError("A user with this email already exists.")
        return value.lower()
    
    def create(self, validated_data):
        user = User.objects.create_user(
            username=validated_data['username'],
            email=validated_data['email'],
            password=validated_data['password'],
            role=validated_data.get('role', User.Role.VIEWER),
        )
        return user
```

**Breaking it down:**

| Part | What it does |
|------|-------------|
| `write_only=True` | The password is accepted in input but NEVER shown in output |
| `read_only_fields` | `id` and `created_at` are auto-generated, not user-provided |
| `validate_email()` | Custom validation: checks email uniqueness |
| `min_length=8` | Built-in validation: password must be ≥ 8 characters |
| `create()` | Custom creation: uses `create_user()` which hashes the password |

### How validation works:

```python
serializer = UserRegistrationSerializer(data=request.data)

if serializer.is_valid():     # ← Runs ALL validations
    user = serializer.save()  # ← Calls create() method
else:
    print(serializer.errors)  # ← Shows what went wrong
    # Example: {"email": ["A user with this email already exists."]}
```

---

## 8. Views (Request Handlers)

### What is a View?

A **view** is a function that:
1. Receives an HTTP request
2. Does something (queries database, runs business logic)
3. Returns an HTTP response

### Function-Based Views (What We Use)

```python
@api_view(['GET', 'POST'])           # Only accept GET and POST methods
@permission_classes([IsActiveUser, ReadOnlyForViewers])  # Check permissions
def record_list_create(request):
    if request.method == 'GET':
        # List records
        records = FinancialRecord.objects.filter(is_deleted=False)
        serializer = FinancialRecordListSerializer(records, many=True)
        return Response({'success': True, 'data': serializer.data})
    
    elif request.method == 'POST':
        # Create a new record
        serializer = FinancialRecordSerializer(data=request.data, context={'request': request})
        if serializer.is_valid():
            serializer.save()
            return Response({'success': True, 'data': serializer.data}, status=201)
        return Response({'success': False, 'error': serializer.errors}, status=400)
```

**Key patterns:**

1. **`@api_view(['GET', 'POST'])`** — Decorator that tells DRF which HTTP methods this view accepts. If someone sends a DELETE request, they get a 405 (Method Not Allowed) automatically.

2. **`@permission_classes([...])`** — Checks permissions BEFORE your code runs. If denied, the function body never executes.

3. **`request.data`** — The parsed JSON body from the request (like a Python dictionary).

4. **`request.user`** — The authenticated user making the request (set by JWT middleware).

5. **`Response({...})`** — Creates a JSON HTTP response.

6. **`many=True`** — Tells the serializer to handle a list of objects, not just one.

---

## 9. URL Routing (The Address System)

### How URLs Map to Views

Django uses a chain of URL patterns to find the right view:

```
Client sends: POST /api/records/

Step 1: finance_backend/urls.py
  path('api/records/', include('records.urls'))
  → Strips "api/records/" and passes "" to records/urls.py

Step 2: records/urls.py
  path('', views.record_list_create)
  → "" matches empty string → calls record_list_create view
```

### URL with parameters:

```
Client sends: GET /api/records/42/

Step 1: finance_backend/urls.py
  path('api/records/', include('records.urls'))
  → Strips "api/records/" and passes "42/" to records/urls.py

Step 2: records/urls.py
  path('<int:record_id>/', views.record_detail)
  → "42/" matches <int:record_id> → calls record_detail(request, record_id=42)
```

The `<int:record_id>` part:
- `int` → only matches integers (not "abc")
- `record_id` → the variable name passed to the view function

---

## 10. Authentication (Who Are You?)

### What is JWT?

**JWT (JSON Web Token)** is a way to prove who you are without sending your password every time.

#### The Flow:

```
1. Login
   POST /api/auth/login/
   {"username": "admin", "password": "admin123456"}
   
   Server: "Credentials valid! Here's your token."
   → Returns: {"access": "eyJhbGci...", "refresh": "eyJhbGci..."}

2. Use the token for everything else
   GET /api/records/
   Authorization: Bearer eyJhbGci...
   
   Server: "I decoded this token. You're admin with role 'admin'. OK, here's your data."
```

#### What's inside a JWT?

A JWT has 3 parts separated by dots: `xxxxx.yyyyy.zzzzz`

1. **Header**: Algorithm used (e.g., HS256)
2. **Payload**: User info (user_id, expiry time)
3. **Signature**: Cryptographic proof that the token wasn't tampered with

```json
// Decoded payload:
{
  "user_id": 1,
  "exp": 1712000000,  // Expiry timestamp
  "token_type": "access"
}
```

#### Access Token vs Refresh Token

| Token | Lifetime | Purpose |
|-------|----------|---------|
| **Access Token** | 1 hour | Used in every API request |
| **Refresh Token** | 1 day | Used to get a new access token without re-logging in |

Why two tokens? Security. If your access token is stolen, it expires in 1 hour. The refresh token is only sent to one endpoint, reducing exposure.

### How JWT Auth Works in Our Code

In `settings.py`:
```python
REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework_simplejwt.authentication.JWTAuthentication',
    ),
    'DEFAULT_PERMISSION_CLASSES': (
        'rest_framework.permissions.IsAuthenticated',
    ),
}
```

This means:
1. **Every request** goes through JWT authentication (reads the `Authorization` header)
2. **By default**, only authenticated users can access endpoints
3. We use `@permission_classes([AllowAny])` on login/register to make them public

---

## 11. Authorization & Permissions (What Can You Do?)

### Authentication vs Authorization

| | Authentication | Authorization |
|---|---|---|
| **Question** | "Who are you?" | "What can you do?" |
| **How** | JWT token | Role-based permissions |
| **Example** | "You are user #1 (admin)" | "Admins can create records" |

### Our Permission Classes (users/permissions.py)

```python
class IsAdmin(BasePermission):
    """Only admins can access."""
    message = "Only administrators can perform this action."
    
    def has_permission(self, request, view):
        return (
            request.user
            and request.user.is_authenticated
            and request.user.role == 'admin'
        )
```

**How it works:**
1. Before your view code runs, DRF calls `has_permission()`
2. If it returns `True` → proceed to the view
3. If it returns `False` → return 403 Forbidden with the `message`

### Permission Classes We Built

| Class | Who it allows | Used where |
|-------|--------------|-----------|
| `IsAdmin` | Admins only | User management endpoints |
| `IsAnalystOrAdmin` | Analysts + Admins | Dashboard analytics |
| `IsActiveUser` | Any active user | All endpoints (checks account isn't deactivated) |
| `ReadOnlyForViewers` | GET for all, write for admins only | Financial records |

### How `ReadOnlyForViewers` Works

```python
class ReadOnlyForViewers(BasePermission):
    def has_permission(self, request, view):
        if not (request.user and request.user.is_authenticated):
            return False
        
        # GET, HEAD, OPTIONS are safe (read-only) methods
        if request.method in ('GET', 'HEAD', 'OPTIONS'):
            return True  # Everyone can read
        
        # POST, PUT, PATCH, DELETE need admin role
        return request.user.role == 'admin'
```

**Real-world analogy:**
- A museum (viewer): You can **look** at the art, but you can't **touch** it
- A curator (admin): You can look AND rearrange/add/remove art

---

## 12. Validation & Error Handling

### Why Validate?

**Never trust user input.** Users might send:
- Empty required fields
- Negative amounts for money
- Invalid dates
- Strings where numbers are expected
- Extremely long text that could crash your database

### Levels of Validation

#### 1. Serializer Field Validation (Automatic)
```python
amount = models.DecimalField(max_digits=12, decimal_places=2)
```
Django automatically rejects: `"abc"`, `null`, values with too many digits.

#### 2. Custom Field Validation
```python
def validate_amount(self, value):
    if value <= Decimal('0'):
        raise serializers.ValidationError("Amount must be a positive number.")
    return value
```

#### 3. Model-Level Validation (Choices)
```python
transaction_type = models.CharField(choices=TransactionType.choices)
```
Only allows "income" or "expense". Anything else is rejected.

### Our Custom Error Handler (users/utils.py)

We override DRF's default error handler to ensure ALL errors have the same JSON structure:

```json
{
    "success": false,
    "error": {
        "code": 400,
        "message": "Bad request. Please check your input.",
        "details": {
            "amount": ["Amount must be a positive number."],
            "category": ["\"invalid\" is not a valid choice."]
        }
    }
}
```

**Why is this important?** Frontend developers love consistent error formats. They can write ONE piece of error-handling code that works for ALL endpoints.

---

## 13. Dashboard Analytics (Aggregation Queries)

### What is Aggregation?

Instead of returning individual records, we calculate **summary statistics** on the server.

**Why on the server?** If you have 100,000 records, you don't want to send all of them to the frontend and calculate totals in JavaScript. That would be slow and wasteful. Instead, the database does the math and sends just the result.

### Example: Summary Endpoint

```python
totals = records.aggregate(
    total_income=Sum('amount', filter=Q(transaction_type='income')),
    total_expenses=Sum('amount', filter=Q(transaction_type='expense')),
    total_records=Count('id'),
)
```

**What this translates to in SQL:**
```sql
SELECT 
    SUM(CASE WHEN transaction_type = 'income' THEN amount END) AS total_income,
    SUM(CASE WHEN transaction_type = 'expense' THEN amount END) AS total_expenses,
    COUNT(id) AS total_records
FROM records_financialrecord
WHERE is_deleted = 0;
```

But you write Python, not SQL! Django's ORM translates it for you.

### Key ORM Concepts Used

| Django ORM | What it does | SQL equivalent |
|-----------|-------------|---------------|
| `Sum('amount')` | Add up all amounts | `SUM(amount)` |
| `Count('id')` | Count rows | `COUNT(id)` |
| `Q(type='income')` | Conditional filter | `WHERE type='income'` |
| `.values('category')` | Group by category | `GROUP BY category` |
| `.annotate(...)` | Add calculated columns | `SELECT ... AS ...` |
| `TruncMonth('date')` | Extract month from date | `DATE_TRUNC('month', date)` |
| `.filter(is_deleted=False)` | Only non-deleted records | `WHERE is_deleted = 0` |

### Category Breakdown Example

```python
breakdown = (
    records
    .values('category')          # GROUP BY category
    .annotate(
        total=Sum('amount'),     # SUM(amount) for each category
        count=Count('id'),       # COUNT records per category
    )
    .order_by('-total')          # Sort by total descending
)
```

Result:
```json
[
    {"category": "salary", "total": "300000.00", "count": 6, "percentage": 45.2},
    {"category": "rent", "total": "90000.00", "count": 6, "percentage": 13.5},
    ...
]
```

---

## 14. Testing (Proving It Works)

### Why Write Tests?

Tests are like a safety net. They:
1. **Prove your code works** — not just "I tried it once and it seemed fine"
2. **Catch regressions** — if you change something and break something else
3. **Document behavior** — tests describe what your code SHOULD do
4. **Give confidence** — you can refactor code without fear

### How Django Tests Work

```python
class AuthenticationTests(TestCase):
    def setUp(self):
        """Runs BEFORE each test method."""
        self.client = APIClient()
        self.test_user = User.objects.create_user(
            username='testuser', email='test@example.com',
            password='testpass123', role='viewer',
        )
    
    def test_login_success(self):
        """Each test method starts with test_"""
        response = self.client.post('/api/auth/login/', {
            'username': 'testuser',
            'password': 'testpass123',
        }, format='json')
        
        self.assertEqual(response.status_code, 200)  # Check status is 200
        self.assertTrue(response.data['success'])     # Check success is True
        self.assertIn('tokens', response.data['data']) # Check tokens exist
```

**Key concepts:**

| Concept | Explanation |
|---------|-------------|
| `TestCase` | Base class that sets up an empty test database |
| `setUp()` | Creates test data before EACH test method |
| `APIClient()` | A fake HTTP client that makes requests to your views |
| `self.assertEqual(a, b)` | Assert that `a` equals `b` |
| `self.assertTrue(x)` | Assert that `x` is True |
| `self.assertIn(a, b)` | Assert that `a` is inside `b` |
| `force_authenticate(user=x)` | Simulate being logged in as user `x` |

### What We Test (41 Tests Total)

**Authentication Tests (11):**
- ✅ Registration with valid data → 201 Created
- ✅ Registration with duplicate email → 400 Bad Request
- ✅ Registration with short password → 400 Bad Request
- ✅ Registration with missing fields → 400 Bad Request
- ✅ Login with valid credentials → 200 OK + tokens
- ✅ Login with wrong password → 401 Unauthorized
- ✅ Login with inactive account → 401 Unauthorized
- ✅ Profile access when authenticated → 200 OK
- ✅ Profile access when not authenticated → 401

**User Management Tests (8):**
- ✅ Admin can list users
- ✅ Viewer cannot list users → 403
- ✅ Analyst cannot list users → 403
- ✅ Admin can change roles
- ✅ Admin cannot change own role → 400
- ✅ Admin can deactivate users
- ✅ Admin can delete users
- ✅ Admin cannot delete self → 400

**Financial Records Tests (14):**
- ✅ Admin can create records
- ✅ Viewer cannot create records → 403
- ✅ Analyst cannot create records → 403
- ✅ Negative amount rejected → 400
- ✅ Invalid transaction type rejected → 400
- ✅ All roles can list records
- ✅ Filtering by type, category works
- ✅ Search by description works
- ✅ Get single record by ID
- ✅ Non-existent record → 404
- ✅ Admin can update records
- ✅ Viewer cannot update → 403
- ✅ Admin can soft-delete records
- ✅ Unauthenticated access → 401

**Dashboard Tests (9):**
- ✅ Summary calculations are accurate
- ✅ Admin can access summary
- ✅ Viewer cannot access summary → 403
- ✅ Category breakdown works
- ✅ Filtered breakdown works
- ✅ Monthly trends work
- ✅ All roles can see recent activity
- ✅ Limit parameter works
- ✅ Unauthenticated access → 401

---

## 15. Key Concepts Summary

### Design Patterns Used

| Pattern | Where | Why |
|---------|-------|-----|
| **MVC (Model-View-Controller)** | Overall architecture | Separates data, logic, presentation |
| **Repository Pattern** | Django ORM | Models abstract database operations |
| **Decorator Pattern** | `@api_view`, `@permission_classes` | Add behavior to functions without modifying them |
| **Factory Pattern** | `create_user()` | Encapsulates complex object creation (password hashing) |
| **Soft Delete** | `is_deleted` flag | Data preservation — never truly lose financial data |

### Key Terminology

| Term | Simple Explanation |
|------|-------------------|
| **API** | A set of URLs that accept/return JSON data (not HTML pages) |
| **REST** | A design style for APIs (uses HTTP methods + URLs meaningfully) |
| **ORM** | Object-Relational Mapping — talk to databases with Python classes |
| **Migration** | Version-controlled database schema changes |
| **Serialization** | Converting Python objects to JSON (and back) |
| **Middleware** | Code that runs on EVERY request (before/after views) |
| **JWT** | A signed token proving who you are |
| **CRUD** | Create, Read, Update, Delete — the 4 basic operations |
| **Aggregation** | Calculating summaries (SUM, COUNT, AVG) from data |
| **Soft Delete** | Marking data as "deleted" without removing it from the database |
| **Pagination** | Splitting large lists into pages (10 items per page) |
| **Foreign Key** | A link between two database tables (record → user) |

---

## 16. How to Run & Test Everything

### First-Time Setup

```bash
# 1. Navigate to the project
cd /Users/mpal_08/Desktop/assisment2

# 2. Install dependencies
pip3 install -r requirements.txt

# 3. Create database tables
python3.10 manage.py migrate

# 4. Load sample data
python3.10 seed_data.py

# 5. Start the server
python3.10 manage.py runserver
```

### Testing with curl

```bash
# 1. Login as admin
curl -s -X POST http://127.0.0.1:8000/api/auth/login/ \
  -H "Content-Type: application/json" \
  -d '{"username":"admin","password":"admin123456"}' | python3 -m json.tool

# Copy the "access" token from the response

# 2. View all records
curl -s http://127.0.0.1:8000/api/records/ \
  -H "Authorization: Bearer YOUR_TOKEN_HERE" | python3 -m json.tool

# 3. Create a record
curl -s -X POST http://127.0.0.1:8000/api/records/ \
  -H "Authorization: Bearer YOUR_TOKEN_HERE" \
  -H "Content-Type: application/json" \
  -d '{"amount":"999.99","transaction_type":"expense","category":"food","date":"2024-03-15","description":"Test"}' | python3 -m json.tool

# 4. View dashboard summary
curl -s http://127.0.0.1:8000/api/dashboard/summary/ \
  -H "Authorization: Bearer YOUR_TOKEN_HERE" | python3 -m json.tool

# 5. Test access control - login as viewer and try to create a record
curl -s -X POST http://127.0.0.1:8000/api/auth/login/ \
  -H "Content-Type: application/json" \
  -d '{"username":"viewer","password":"viewer123456"}' | python3 -m json.tool

# Use the viewer's token to try creating a record (should fail with 403)
curl -s -X POST http://127.0.0.1:8000/api/records/ \
  -H "Authorization: Bearer VIEWER_TOKEN_HERE" \
  -H "Content-Type: application/json" \
  -d '{"amount":"100","transaction_type":"expense","category":"food","date":"2024-03-15"}' | python3 -m json.tool
```

### Running Automated Tests

```bash
# Run all 41 tests
python3.10 manage.py test --verbosity=2

# Run only specific app tests
python3.10 manage.py test users --verbosity=2
python3.10 manage.py test records --verbosity=2
python3.10 manage.py test dashboard --verbosity=2
```

### Expected Output
```
Ran 41 tests in 13.xxx s

OK
```

---

## That's It! 🎉

You now understand:
- ✅ What a backend is and how it works
- ✅ How HTTP requests flow through Django
- ✅ How databases store data using models
- ✅ How serializers validate and transform data
- ✅ How views process requests and return responses
- ✅ How JWT authentication proves identity
- ✅ How role-based permissions control access
- ✅ How aggregation queries power dashboards
- ✅ How automated tests verify everything works

The best way to learn more: **change something and see what happens!** Break things, fix them, and understand why.
