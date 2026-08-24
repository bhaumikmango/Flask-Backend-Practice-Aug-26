document.addEventListener('DOMContentLoaded', () => {
    // Auth State Management
    let token = localStorage.getItem('token') || null;

    // Elements
    const authDot = document.getElementById('auth-dot');
    const authStatusText = document.getElementById('auth-status-text');
    const logoutBtn = document.getElementById('logout-btn');
    const consoleOutput = document.getElementById('console-output').querySelector('code');
    const responseStatus = document.getElementById('response-status');
    const responseTimeText = document.getElementById('response-time');
    const clearConsoleBtn = document.getElementById('clear-console-btn');

    // Forms & Inputs
    const loginForm = document.getElementById('login-form');
    const createUserForm = document.getElementById('create-user-form');
    const listUsersBtn = document.getElementById('list-users-btn');
    const targetUserIdInput = document.getElementById('target-user-id');
    const getUserBtn = document.getElementById('get-user-btn');
    const deleteUserBtn = document.getElementById('delete-user-btn');
    const updateUserForm = document.getElementById('update-user-form');

    const createPostForm = document.getElementById('create-post-form');
    const listPostsBtn = document.getElementById('list-posts-btn');
    const latestPostBtn = document.getElementById('latest-post-btn');
    const targetPostIdInput = document.getElementById('target-post-id');
    const getPostBtn = document.getElementById('get-post-btn');
    const deletePostBtn = document.getElementById('delete-post-btn');
    const updatePostForm = document.getElementById('update-post-form');

    // Update Auth UI State
    function updateAuthUI() {
        if (token) {
            authDot.classList.add('online');
            authStatusText.textContent = 'Authenticated';
            logoutBtn.classList.remove('hidden');
        } else {
            authDot.classList.remove('online');
            authStatusText.textContent = 'Not Authenticated';
            logoutBtn.classList.add('hidden');
        }
    }

    // Set Token
    function setToken(newToken) {
        token = newToken;
        if (newToken) {
            localStorage.setItem('token', newToken);
        } else {
            localStorage.removeItem('token');
        }
        updateAuthUI();
    }

    // Logout
    logoutBtn.addEventListener('click', () => {
        setToken(null);
        logOutput({ message: "Logged out. Token removed." }, 200, 0);
    });

    // Helper to log requests to console
    function logOutput(data, status, duration) {
        responseStatus.textContent = status || '-';
        responseTimeText.textContent = duration ? `${duration}ms` : '-';
        
        // Color coding status
        if (status >= 200 && status < 300) {
            responseStatus.style.color = 'var(--color-success)';
        } else if (status >= 400) {
            responseStatus.style.color = 'var(--color-danger)';
        } else {
            responseStatus.style.color = 'var(--text-primary)';
        }

        consoleOutput.textContent = JSON.stringify(data, null, 2);
    }

    // Generic Request Wrapper
    async function makeRequest(url, method = 'GET', body = null, isFormData = false) {
        const startTime = Date.now();
        const headers = {};
        
        if (token) {
            headers['Authorization'] = `Bearer ${token}`;
        }

        let requestBody = body;

        if (body && !isFormData) {
            headers['Content-Type'] = 'application/json';
            requestBody = JSON.stringify(body);
        }

        try {
            const options = { method, headers };
            if (requestBody) {
                options.body = requestBody;
            }

            const response = await fetch(url, options);
            const duration = Date.now() - startTime;
            
            let data = null;
            if (response.status !== 204) {
                try {
                    data = await response.json();
                } catch (e) {
                    data = { message: "Invalid JSON response" };
                }
            } else {
                data = { message: "Success (No Content)" };
            }

            logOutput(data, response.status, duration);
            return { status: response.status, data };
        } catch (error) {
            const duration = Date.now() - startTime;
            logOutput({ error: error.message }, 500, duration);
            return { status: 500, data: null };
        }
    }

    // Clear Console
    clearConsoleBtn.addEventListener('click', () => {
        logOutput({ message: "Console cleared." }, null, null);
    });

    // ==================== AUTHENTICATION ====================
    loginForm.addEventListener('submit', async (e) => {
        e.preventDefault();
        const username = document.getElementById('login-username').value;
        const password = document.getElementById('login-password').value;

        // Backend login accepts form-data (oauth2 spec)
        const formData = new FormData();
        formData.append('username', username);
        formData.append('password', password);

        const startTime = Date.now();
        try {
            const response = await fetch('/login', {
                method: 'POST',
                body: formData
            });
            const duration = Date.now() - startTime;
            const data = await response.json();

            logOutput(data, response.status, duration);

            if (response.ok && data.access_token) {
                setToken(data.access_token);
            } else {
                setToken(null);
            }
        } catch (error) {
            logOutput({ error: error.message }, 500, Date.now() - startTime);
            setToken(null);
        }
    });

    // ==================== USER OPERATIONS ====================
    createUserForm.addEventListener('submit', async (e) => {
        e.preventDefault();
        const email = document.getElementById('user-email').value;
        const password = document.getElementById('user-password').value;

        await makeRequest('/users/', 'POST', { email, password });
    });

    listUsersBtn.addEventListener('click', async () => {
        await makeRequest('/users/', 'GET');
    });

    getUserBtn.addEventListener('click', async () => {
        const id = targetUserIdInput.value;
        if (!id) return alert('Please enter a User ID');
        await makeRequest(`/users/${id}`, 'GET');
    });

    deleteUserBtn.addEventListener('click', async () => {
        const id = targetUserIdInput.value;
        if (!id) return alert('Please enter a User ID');
        if (confirm(`Are you sure you want to delete user ${id}?`)) {
            await makeRequest(`/users/${id}`, 'DELETE');
        }
    });

    updateUserForm.addEventListener('submit', async (e) => {
        e.preventDefault();
        const id = targetUserIdInput.value;
        if (!id) return alert('Please enter a User ID first in the input above.');
        
        const email = document.getElementById('update-user-email').value;
        const password = document.getElementById('update-user-password').value;

        await makeRequest(`/users/${id}`, 'PUT', { email, password });
    });

    // ==================== POST OPERATIONS ====================
    createPostForm.addEventListener('submit', async (e) => {
        e.preventDefault();
        const title = document.getElementById('post-title').value;
        const content = document.getElementById('post-content').value;
        const published = document.getElementById('post-published').checked;

        await makeRequest('/posts/', 'POST', { title, content, published });
    });

    listPostsBtn.addEventListener('click', async () => {
        await makeRequest('/posts/', 'GET');
    });

    latestPostBtn.addEventListener('click', async () => {
        await makeRequest('/posts/latest', 'GET');
    });

    getPostBtn.addEventListener('click', async () => {
        const id = targetPostIdInput.value;
        if (!id) return alert('Please enter a Post ID');
        await makeRequest(`/posts/${id}`, 'GET');
    });

    deletePostBtn.addEventListener('click', async () => {
        const id = targetPostIdInput.value;
        if (!id) return alert('Please enter a Post ID');
        if (confirm(`Are you sure you want to delete post ${id}?`)) {
            await makeRequest(`/posts/${id}`, 'DELETE');
        }
    });

    updatePostForm.addEventListener('submit', async (e) => {
        e.preventDefault();
        const id = targetPostIdInput.value;
        if (!id) return alert('Please enter a Post ID first in the input above.');

        const title = document.getElementById('update-post-title').value;
        const content = document.getElementById('update-post-content').value;
        const published = document.getElementById('update-post-published').checked;

        await makeRequest(`/posts/${id}`, 'PUT', { title, content, published });
    });

    // Initialize UI Auth Status
    updateAuthUI();
});
