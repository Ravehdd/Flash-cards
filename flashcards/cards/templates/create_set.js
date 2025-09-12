const API_BASE_URL = 'http://localhost:8000/';
let authToken = localStorage.getItem('authToken');
let currentUser = localStorage.getItem('currentUser');

// Инициализация страницы
document.addEventListener('DOMContentLoaded', function() {
    checkAuthStatus();
    setupEventListeners();
});

function checkAuthStatus() {
    const authSection = document.getElementById('authSection');
    const createSection = document.getElementById('createSection');
    const usernameSpan = document.getElementById('username');
    const logoutBtn = document.getElementById('logoutBtn');

    if (authToken && currentUser) {
        // Пользователь авторизован
        authSection.style.display = 'none';
        createSection.style.display = 'block';
        usernameSpan.textContent = currentUser;
        logoutBtn.style.display = 'inline-block';
    } else {
        // Пользователь не авторизован
        authSection.style.display = 'block';
        createSection.style.display = 'none';
        logoutBtn.style.display = 'none';
    }
}

function setupEventListeners() {
    // Форма входа
    document.getElementById('loginForm').addEventListener('submit', handleLogin);
    
    // Форма создания набора
    document.getElementById('createSetForm').addEventListener('submit', handleCreateSet);
    
    // Кнопка выхода
    document.getElementById('logoutBtn').addEventListener('click', handleLogout);
}

async function handleLogin(e) {
    e.preventDefault();
    
    const username = document.getElementById('usernameInput').value;
    const password = document.getElementById('passwordInput').value;
    
    try {
        const response = await fetch(`${API_BASE_URL}auth/token/login/`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                username: username,
                password: password
            })
        });

        if (response.ok) {
            const data = await response.json();
            console.log(data)
            authToken = data.auth_token;
            currentUser = username;
            console.log("Token", authToken )
            
            // Сохраняем в localStorage
            localStorage.setItem('authToken', authToken);
            localStorage.setItem('currentUser', currentUser);
            
            showMessage('Успешный вход!', 'success');
            checkAuthStatus();
            
            // Очищаем форму входа
            document.getElementById('loginForm').reset();
            
        } else {
            const errorData = await response.json();
            showMessage(`Ошибка входа: ${errorData.detail || 'Неверные данные'}`, 'error');
        }
    } catch (error) {
        showMessage('Ошибка сети или сервера', 'error');
        console.error('Login error:', error);
    }
}

async function handleCreateSet(e) {
    e.preventDefault();
    
    if (!authToken) {
        showMessage('Сначала войдите в систему', 'error');
        return;
    }
    
    const form = e.target;
    const formData = new FormData(form);
    
    const setData = {
        name: formData.get('name'),
        description: formData.get('description') || '',
        category: formData.get('category') || null,
        difficulty: formData.get('difficulty'),
        is_public: formData.get('is_public') === 'on'
    };
    
    // Валидация
    if (!setData.name.trim()) {
        showMessage('Название набора обязательно', 'error');
        return;
    }
    
    try {
        // Показываем loading state
        form.classList.add('loading');
        console.log(authToken)
        const response = await fetch(`${API_BASE_URL}api/sets/create/`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Token ${authToken}`
            },
            body: JSON.stringify(setData)
        });

        if (response.ok) {
            const result = await response.json();
            showMessage(`Набор "${result.name}" успешно создан!`, 'success');
            form.reset();
        } else {
            const errorData = await response.json();
            showMessage(`Ошибка создания: ${errorData.error || errorData.detail || 'Неизвестная ошибка'}`, 'error');
        }
    } catch (error) {
        showMessage('Ошибка сети или сервера', 'error');
        console.error('Create set error:', error);
    } finally {
        form.classList.remove('loading');
    }
}

function handleLogout() {
    authToken = null;
    currentUser = null;
    localStorage.removeItem('authToken');
    localStorage.removeItem('currentUser');
    showMessage('Вы вышли из системы', 'info');
    checkAuthStatus();
}

function showMessage(text, type = 'info') {
    const messageDiv = document.getElementById('message');
    messageDiv.textContent = text;
    messageDiv.className = `message ${type}`;
    
    // Автоскрытие для успешных сообщений
    if (type === 'success') {
        setTimeout(() => {
            messageDiv.textContent = '';
            messageDiv.className = 'message';
        }, 3000);
    }
}

function clearForm() {
    document.getElementById('createSetForm').reset();
    showMessage('Форма очищена', 'info');
}

// Обработка ошибок сети
window.addEventListener('online', () => {
    showMessage('Соединение восстановлено', 'success');
});

window.addEventListener('offline', () => {
    showMessage('Отсутствует интернет-соединение', 'error');
});

// Экспортируем функции для тестирования
if (typeof module !== 'undefined' && module.exports) {
    module.exports = {
        handleLogin,
        handleCreateSet,
        handleLogout,
        showMessage
    };
}