# Finance Dashboard Frontend

This is a premium, vanilla HTML/CSS/JavaScript single-page application built to interface with the Django REST API Backend.

## Features
- **Zero Dependencies**: Built with Vanilla JS, no React, Vue, or Webpack required.
- **Glassmorphism UI**: Beautiful, blurry, semi-transparent overlays matching modern design trends.
- **Token Auth Mechanism**: Connects seamlessly with the backend's JWT authentication system.
- **Role-based Rendering**: Hide/show elements (like the New Record button) strictly based on the user's role. 

## How to Run
It's incredibly simple because it's just static files!

1. **Make sure your backend is running first**:
   ```bash
   cd /Users/mpal_08/Desktop/assisment2
   python3 manage.py runserver 8081
   ```

2. **Open the Frontend**:
   Simply double-click the `index.html` file inside the `frontend/` folder to open it in your browser.
   
   Alternatively, run a quick static server from the terminal:
   ```bash
   cd /Users/mpal_08/Desktop/assisment2/frontend
   python3 -m http.server 8000
   ```
   Then open `http://localhost:8000` in your web browser.

## Test Accounts
Use the same accounts from the Backend Seed data:
- `admin` : `admin123456`
- `analyst` : `analyst123456`
- `viewer` : `viewer123456`
