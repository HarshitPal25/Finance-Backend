# 🎨 Frontend Architecture & Integration Guide

Welcome to the **Frontend Guide**! This document explains how the beautiful, glassmorphism-styled UI we just built hooks up perfectly with the Django backend. 

If you are explaining this project to an interviewer, this guide is your secret weapon.

---

## 1. The Core Philosophy (Why Vanilla?)

We built this entire frontend using **Vanilla HTML, CSS, and JavaScript**. There is no React, no Angular, no Vue, and no Tailwind CSS. 

**Why point this out to an interviewer?** 
Because it demonstrates **first-principles engineering**. Before relying on heavy frameworks, you understand exactly how the web actually works under the hood. You know how browsers manipulate the DOM (Document Object Model) and how native `fetch()` calls work.

---

## 2. Breaking Down the Stack

### 📂 `index.html` (The Skeleton)
The HTML file defines the structure. 
We used a **Single Page Application (SPA)** approach. Instead of redirecting the user to `login.html` and then `dashboard.html`, everything exists in one file. 

Look at the structure in `index.html`:
```html
<div id="login-container"> ... </div>
<div id="app-container" class="hidden"> ... </div>
```
When a user logs in successfully, JavaScript simply throws a `hidden` CSS class onto the login container, and removes it from the app container. This creates an instant, seamless transition.

### 🎨 `styles.css` (The Skin)
To meet the requirement of a **premium, wow-inducing aesthetic**, we implemented **Glassmorphism**. 
This is achieved combining three CSS properties:
1. `background: rgba(15, 17, 26, 0.6);` (Transparent dark background)
2. `backdrop-filter: blur(16px);` (The magic blur effect)
3. Animated gradient blobs lingering *behind* the elements.

We also strictly used CSS custom variables (`:root { --primary: #6c63ff; }`) to maintain design consistency without needing an external library.

### 🧠 `app.js` (The Brain)
This is where the magic happens. The JavaScript file acts as the bridge connecting our HTML inputs to the Django server.

---

## 3. How the Frontend Talks to the Backend (The Fetch API)

When you make a change in the frontend (like clicking "Sign In" or "Save Transaction"), `app.js` needs to tell the backend about it over the internet.

We do this using JavaScript's native `fetch` protocol. 

### Step 1: The Login Dance
When you type your username and hit submit, `app.js` intercepts that click.

1. It packages the data into a JSON string.
2. It sends an HTTP POST request to Django's `http://127.0.0.1:8081/api/auth/login/`.
3. The Django backend validates the user and responds with a **JWT Token**.

### Step 2: Saving the VIP Pass (Token Storage)
If the login succeeds, the frontend needs to remember who we are. 
```javascript
localStorage.setItem('access_token', result.data.tokens.access);
```
We save the token in the browser's `localStorage`. Even if you hit the refresh button, the browser remembers you are logged in.

### Step 3: Making Authorized Requests
Once we have that token, every single subsequent request needs to wear it like a nametag. 

In `app.js`, we built a helper function called `apiFetch`:
```javascript
const headers = {
    'Authorization': `Bearer ${authToken}`, // <--- The Nametag
    'Content-Type': 'application/json'
};
```
When `app.js` needs the dashboard math, it `fetch`es `/dashboard/summary/` and attaches that header. Django sees the header, says "Oh, it's the Admin!", runs the math, and sends the numbers back.

---

## 4. Frontend Role-Based Access Control (RBAC)

Our backend strictly enforces rules (e.g. Viewers can't create records). However, it's terrible user-experience to let a Viewer see an "Add Record" button, click it, and THEN get an error.

The frontend handles this gracefully by looking at the `currentUser.role` variable.
```javascript
if (currentUser.role === 'admin') {
    addBtn.classList.remove('hidden');
} else {
    // If you are a viewer or analyst, the button literally disappears
    addBtn.classList.add('hidden'); 
}
```

Similarly, if you log in as a Viewer, the frontend doesn't even attempt to fetch the mathematical summary (because it knows the backend will reject it). Instead, it obfuscates the numbers on the screen to say "Locked."

---

## 5. Security Note: CORS

When we started building the frontend, we had to change the backend `settings.py` to include `django-cors-headers`. Why?

**CORS (Cross-Origin Resource Sharing)** is a browser security mechanism. 
By default, if your frontend is running on `http://localhost:8000` but tries to fetch data from your API at `http://127.0.0.1:8081`, your browser will actively block the connection. This prevents malicious websites from silently grabbing data from other tabs you have open.

By adding `CORS_ALLOW_ALL_ORIGINS = True` to Django, we explicitly told the browser: *"It's okay, we trust who is talking to us."* (Note: in production, you would lock this down to just your actual website URL).

---

## Summary for the Interview

If asked about the frontend, hit these points:
1. **Tech Stack:** "I built a dedicated SPA using vanilla HTML/JS/CSS to showcase native DOM manipulation without heavy frameworks."
2. **Design System:** "I utilized CSS variables and backdrop-filters to create a modern Glassmorphism aesthetic."
3. **State Management:** "I managed authentication state using `localStorage` and native Fetch interceptors with Bearer token headers."
4. **UX Guardrails:** "The UI dynamically adapts to the user's role payload in the JWT token (hiding admin-level buttons from standard viewers) to prevent bad API requests before they even happen."
