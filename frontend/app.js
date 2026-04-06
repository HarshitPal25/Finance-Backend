// State and Configuration
const API_BASE = 'http://127.0.0.1:8081/api';
let authToken = localStorage.getItem('access_token') || null;
let currentUser = JSON.parse(localStorage.getItem('user_data')) || null;

// DOM Elements
const loginContainer = document.getElementById('login-container');
const appContainer = document.getElementById('app-container');
const loginForm = document.getElementById('login-form');
const loginError = document.getElementById('login-error');
const logoutBtn = document.getElementById('logout-btn');

const viewDashboard = document.getElementById('view-dashboard');
const viewRecords = document.getElementById('view-records');
const viewUsers = document.getElementById('view-users');
const navUsers = document.getElementById('nav-users');
const navItems = document.querySelectorAll('.nav-item');

// Init
function init() {
    document.getElementById('date-display').innerText = new Date().toLocaleDateString('en-US', { weekday: 'long', year: 'numeric', month: 'long', day: 'numeric' });
    
    if (authToken && currentUser) {
        showApp();
    } else {
        showLogin();
    }
}

// --- UI Navigation ---
function showLogin() {
    loginContainer.classList.remove('hidden');
    appContainer.classList.add('hidden');
}

function showApp() {
    loginContainer.classList.add('hidden');
    appContainer.classList.remove('hidden');
    
    // Update user profile display
    document.getElementById('display-username').innerText = currentUser.username;
    document.getElementById('display-role').innerText = currentUser.role;
    document.getElementById('user-avatar').innerText = currentUser.username.charAt(0).toUpperCase();

    // Show/hide Admin-only buttons
    const addBtn = document.getElementById('add-record-btn');
    if (currentUser.role === 'admin') {
        addBtn.classList.remove('hidden');
        navUsers.classList.remove('hidden');
    } else {
        addBtn.classList.add('hidden');
        navUsers.classList.add('hidden');
    }

    // Load initial data
    loadDashboardData();
}

function switchView(viewName) {
    // Update Nav
    navItems.forEach(nav => {
        if(nav.dataset.view === viewName) nav.classList.add('active');
        else nav.classList.remove('active');
    });

    // Update Pages
    viewDashboard.classList.add('hidden');
    viewRecords.classList.add('hidden');
    viewUsers.classList.add('hidden');

    if (viewName === 'dashboard') {
        viewDashboard.classList.remove('hidden');
        document.getElementById('page-title').innerText = 'Dashboard Overview';
        loadDashboardData();
    } else if (viewName === 'records') {
        viewRecords.classList.remove('hidden');
        document.getElementById('page-title').innerText = 'Transaction History';
        loadRecords();
    } else if (viewName === 'users') {
        viewUsers.classList.remove('hidden');
        document.getElementById('page-title').innerText = 'System Users';
        loadUsers();
    }
}

// --- Auth API ---
loginForm.addEventListener('submit', async (e) => {
    e.preventDefault();
    const username = document.getElementById('username').value;
    const password = document.getElementById('password').value;
    const btn = loginForm.querySelector('button');
    
    btn.innerText = 'Signing In...';
    btn.disabled = true;

    try {
        const response = await fetch(`${API_BASE}/auth/login/`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ username, password })
        });
        const result = await response.json();

        if (result.success) {
            authToken = result.data.tokens.access;
            currentUser = result.data.user;
            localStorage.setItem('access_token', authToken);
            localStorage.setItem('user_data', JSON.stringify(currentUser));
            showApp();
        } else {
            loginError.innerText = result.error.message || 'Login failed';
        }
    } catch (error) {
        loginError.innerText = 'Network error. Is the server running?';
    } finally {
        btn.innerText = 'Sign In';
        btn.disabled = false;
    }
});

logoutBtn.addEventListener('click', () => {
    authToken = null;
    currentUser = null;
    localStorage.removeItem('access_token');
    localStorage.removeItem('user_data');
    showLogin();
});

// --- API Helpers ---
async function apiFetch(endpoint, options = {}) {
    if (!authToken) return null;
    
    const headers = {
        'Authorization': `Bearer ${authToken}`,
        'Content-Type': 'application/json',
        ...options.headers
    };

    try {
        const res = await fetch(`${API_BASE}${endpoint}`, { ...options, headers });
        if (res.status === 401) {
            logoutBtn.click(); // Auto-logout if token expired
            return null;
        }
        return await res.json();
    } catch (err) {
        console.error('API Fetch Error:', err);
        return { success: false, error: { message: "Network error" } };
    }
}

function showNotification(msg, type) {
    const banner = document.getElementById('notification');
    banner.innerText = msg;
    banner.className = `notification ${type}`;
    setTimeout(() => { banner.classList.add('hidden'); }, 3000);
}

// --- Dashboard Logic ---
async function loadDashboardData() {
    // Only Analysts & Admins can view summary maths
    if (currentUser.role === 'admin' || currentUser.role === 'analyst') {
        fetchSummary();
        fetchCategoryBreakdown();
    } else {
        // Obfuscate for Viewers
        document.getElementById('total-income').innerText = 'Locked';
        document.getElementById('total-expenses').innerText = 'Locked';
        document.getElementById('net-balance').innerText = 'Locked';
        document.getElementById('category-breakdown-list').innerHTML = '<p class="text-muted text-center">Upgrade to Analyst to view categories.</p>';
    }

    // Everyone can view recent activity
    fetchRecentActivity();
}

async function fetchSummary() {
    const data = await apiFetch('/dashboard/summary/');
    if (data && data.success) {
        document.getElementById('total-income').innerText = `₹${data.data.total_income}`;
        document.getElementById('total-expenses').innerText = `₹${data.data.total_expenses}`;
        document.getElementById('net-balance').innerText = `₹${data.data.net_balance}`;
    }
}

async function fetchCategoryBreakdown() {
    const list = document.getElementById('category-breakdown-list');
    list.innerHTML = '<div class="loading-spinner"></div>';
    
    const data = await apiFetch('/dashboard/category-breakdown/');
    if (data && data.success && data.data.breakdown) {
        list.innerHTML = '';
        data.data.breakdown.forEach(item => {
            const el = document.createElement('div');
            el.className = 'category-item';
            el.innerHTML = `
                <div class="item-left">
                    <span class="item-title">${item.category_display}</span>
                    <div class="progress-bar-bg">
                        <div class="progress-bar-fill" style="width: ${item.percentage}%"></div>
                    </div>
                </div>
                <div class="item-right text-right">
                    <div class="item-amount">₹${item.total}</div>
                    <div class="item-sub">${item.percentage}%</div>
                </div>
            `;
            list.appendChild(el);
        });
    }
}

async function fetchRecentActivity() {
    const list = document.getElementById('recent-activity-list');
    list.innerHTML = '<div class="loading-spinner"></div>';
    
    const data = await apiFetch('/dashboard/recent-activity/?limit=5');
    if (data && data.success && data.data) {
        list.innerHTML = '';
        data.data.forEach(item => {
            const isInc = item.transaction_type === 'income';
            const el = document.createElement('div');
            el.className = 'transaction-item';
            el.innerHTML = `
                <div class="item-left">
                    <span class="item-title">${item.category_display}</span>
                    <span class="item-sub">${new Date(item.date).toLocaleDateString()}</span>
                </div>
                <div class="item-amount ${isInc ? 'amount-income' : 'amount-expense'}">
                    ${isInc ? '+' : '-'}₹${item.amount}
                </div>
            `;
            list.appendChild(el);
        });
    }
}

// --- Records Logic ---
async function loadRecords(searchQuery = '') {
    const tbody = document.getElementById('records-table-body');
    tbody.innerHTML = '<tr><td colspan="5" style="text-align: center;"><div class="loading-spinner"></div></td></tr>';

    let url = '/records/?page_size=20';
    if (searchQuery) url += `&search=${encodeURIComponent(searchQuery)}`;

    const data = await apiFetch(url);
    if (data && data.success) {
        tbody.innerHTML = '';
        data.data.forEach(record => {
            const isInc = record.transaction_type === 'income';
            const tr = document.createElement('tr');
            tr.innerHTML = `
                <td>${new Date(record.date).toLocaleDateString()}</td>
                <td><span class="${isInc ? 'badge-income' : 'badge-expense'}">${record.transaction_type}</span></td>
                <td>${record.category.toUpperCase()}</td>
                <td>${record.description || '-'}</td>
                <td class="text-right ${isInc ? 'amount-income' : 'amount-expense'}">
                    ${isInc ? '+' : '-'}₹${record.amount}
                </td>
            `;
            tbody.appendChild(tr);
        });
    }
}

// Handle search
const searchInput = document.getElementById('record-search');
let searchTimeout;
searchInput.addEventListener('input', (e) => {
    clearTimeout(searchTimeout);
    searchTimeout = setTimeout(() => {
        loadRecords(e.target.value);
    }, 500); // 500ms debounce
});

// --- Modal & Form Logic (Admin Only) ---
const recordModal = document.getElementById('record-modal');
const recordForm = document.getElementById('record-form');
const addRecordBtn = document.getElementById('add-record-btn');
const closeModalBtn = document.getElementById('close-modal');
const cancelModalBtn = document.getElementById('cancel-modal');

addRecordBtn.addEventListener('click', () => { recordModal.classList.remove('hidden'); });
closeModalBtn.addEventListener('click', () => { recordModal.classList.add('hidden'); });
cancelModalBtn.addEventListener('click', () => { recordModal.classList.add('hidden'); });

recordForm.addEventListener('submit', async (e) => {
    e.preventDefault();
    const btn = recordForm.querySelector('button[type="submit"]');
    btn.innerText = 'Saving...';
    btn.disabled = true;

    const payload = {
        transaction_type: document.getElementById('record-type').value,
        category: document.getElementById('record-category').value,
        amount: document.getElementById('record-amount').value,
        date: document.getElementById('record-date').value,
        description: document.getElementById('record-description').value
    };

    const data = await apiFetch('/records/', {
        method: 'POST',
        body: JSON.stringify(payload)
    });

    if (data && data.success) {
        recordModal.classList.add('hidden');
        recordForm.reset();
        showNotification('Record added successfully!', 'success');
        loadRecords(); // Refresh table
    } else {
        document.getElementById('form-error').innerText = data.error.message || 'Failed to save';
    }

    btn.innerText = 'Save Transaction';
    btn.disabled = false;
});

// Navigation bindings
navItems.forEach(nav => {
    nav.addEventListener('click', (e) => {
        e.preventDefault();
        switchView(e.target.dataset.view);
    });
});

// Start App
init();

// --- Users Logic (Admin Only) ---
async function loadUsers() {
    const tbody = document.getElementById('users-table-body');
    tbody.innerHTML = '<tr><td colspan="5" style="text-align: center;"><div class="loading-spinner"></div></td></tr>';

    const data = await apiFetch('/users/');
    if (data && data.success) {
        tbody.innerHTML = '';
        data.data.forEach(user => {
            const tr = document.createElement('tr');
            tr.innerHTML = `
                <td>${user.username}</td>
                <td>${user.email}</td>
                <td>
                    <select class="role-select" data-id="${user.id}" ${user.id === currentUser.id ? 'disabled' : ''}>
                        <option value="viewer" ${user.role === 'viewer' ? 'selected' : ''}>Viewer</option>
                        <option value="analyst" ${user.role === 'analyst' ? 'selected' : ''}>Analyst</option>
                        <option value="admin" ${user.role === 'admin' ? 'selected' : ''}>Admin</option>
                    </select>
                </td>
                <td>
                    <button class="btn-secondary status-btn" data-id="${user.id}" data-active="${user.is_active}" ${user.id === currentUser.id ? 'disabled' : ''} style="padding: 0.3rem 0.6rem; font-size: 0.8rem; background: ${user.is_active ? 'rgba(0, 210, 137, 0.2)' : 'rgba(255, 77, 109, 0.2)'}; color: ${user.is_active ? 'var(--success)' : 'var(--danger)'}; border: 1px solid transparent;">
                        ${user.is_active ? 'Active' : 'Inactive'}
                    </button>
                </td>
                <td class="text-right">
                    <button class="delete-btn" data-id="${user.id}" ${user.id === currentUser.id ? 'disabled' : ''} style="background: none; border: none; color: var(--danger); cursor: ${user.id === currentUser.id ? 'not-allowed' : 'pointer'}; padding: 0.5rem; opacity: ${user.id === currentUser.id ? '0.5' : '1'};">
                        Delete
                    </button>
                </td>
            `;
            tbody.appendChild(tr);
        });

        // Add event listeners to new elements
        document.querySelectorAll('.role-select').forEach(select => {
            select.addEventListener('change', async (e) => {
                const userId = e.target.dataset.id;
                const newRole = e.target.value;
                const res = await apiFetch(`/users/${userId}/role/`, {
                    method: 'PUT',
                    body: JSON.stringify({ role: newRole })
                });
                if (res && res.success) showNotification('Role updated!', 'success');
                else { showNotification(res?.error?.message || 'Update failed', 'error'); loadUsers(); }
            });
        });

        document.querySelectorAll('.status-btn').forEach(btn => {
            btn.addEventListener('click', async (e) => {
                const userId = e.target.dataset.id;
                const isActive = e.target.dataset.active === 'true';
                const res = await apiFetch(`/users/${userId}/status/`, {
                    method: 'PUT',
                    body: JSON.stringify({ is_active: !isActive })
                });
                if (res && res.success) {
                    showNotification('Status updated!', 'success');
                    loadUsers();
                } else showNotification(res?.error?.message || 'Update failed', 'error');
            });
        });

        document.querySelectorAll('.delete-btn').forEach(btn => {
            btn.addEventListener('click', async (e) => {
                if(!confirm('Are you sure you want to delete this user?')) return;
                const userId = e.target.dataset.id;
                const res = await apiFetch(`/users/${userId}/delete/`, { method: 'DELETE' });
                if (res && res.success) {
                    showNotification('User deleted!', 'success');
                    loadUsers();
                } else showNotification(res?.error?.message || 'Delete failed', 'error');
            });
        });
    }
}
