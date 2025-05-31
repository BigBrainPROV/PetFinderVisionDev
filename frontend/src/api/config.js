import axios from 'axios';
import environment from '../config/environment';

const api = axios.create({
    baseURL: environment.apiUrl,
    headers: {
        'Content-Type': 'application/json',
    },
    // Не устанавливаем Content-Type по умолчанию, чтобы axios мог автоматически установить правильный заголовок для multipart/form-data
});

// Флаг для отслеживания процесса обновления токена
let isRefreshing = false;
let failedQueue = [];

const processQueue = (error, token = null) => {
    failedQueue.forEach(prom => {
        if (error) {
            prom.reject(error);
        } else {
            prom.resolve(token);
        }
    });
    failedQueue = [];
};

// Добавляем перехватчик для добавления токена к каждому запросу
api.interceptors.request.use(
    (config) => {
        console.log('API Request Config:', {
            url: config.url,
            method: config.method,
            headers: config.headers,
        });
        
        const token = localStorage.getItem('jwtToken');
        if (token) {
            config.headers.Authorization = `Bearer ${token}`;
        }
        return config;
    },
    (error) => {
        console.error('API Request Error:', error);
        return Promise.reject(error);
    }
);

// Добавляем перехватчик для обработки ответов
api.interceptors.response.use(
    (response) => {
        return response;
    },
    async (error) => {
        console.error('API Error:', error);
        
        const originalRequest = error.config;

        // Если есть ответ от сервера
        if (error.response) {
            console.error('Error response:', {
                status: error.response.status,
                data: error.response.data,
                headers: error.response.headers,
            });

            // Проверяем, является ли ошибка связанной с истечением токена
            if (error.response.status === 401 && !originalRequest._retry) {
                if (isRefreshing) {
                    // Если уже идет процесс обновления, добавляем запрос в очередь
                    return new Promise((resolve, reject) => {
                        failedQueue.push({ resolve, reject });
                    })
                        .then(token => {
                            originalRequest.headers['Authorization'] = `Bearer ${token}`;
                            return api(originalRequest);
                        })
                        .catch(err => Promise.reject(err));
                }

                originalRequest._retry = true;
                isRefreshing = true;

                // Пытаемся обновить токен
                const refreshToken = localStorage.getItem('refreshToken');
                if (!refreshToken) {
                    // Если нет refresh токена, выходим из системы
                    localStorage.removeItem('jwtToken');
                    localStorage.removeItem('currentUser');
                    window.location.href = '/login';
                    return Promise.reject(error);
                }

                try {
                    const response = await api.post('/api/token/refresh/', {
                        refresh: refreshToken
                    });

                    if (response.data.access) {
                        const newToken = response.data.access;
                        localStorage.setItem('jwtToken', newToken);
                        api.defaults.headers.common['Authorization'] = `Bearer ${newToken}`;
                        
                        // Обрабатываем очередь запросов
                        processQueue(null, newToken);
                        
                        // Повторяем оригинальный запрос с новым токеном
                        originalRequest.headers['Authorization'] = `Bearer ${newToken}`;
                        return api(originalRequest);
                    }
                } catch (refreshError) {
                    processQueue(refreshError, null);
                    // Если не удалось обновить токен, выходим из системы
                    localStorage.removeItem('jwtToken');
                    localStorage.removeItem('refreshToken');
                    localStorage.removeItem('currentUser');
                    window.location.href = '/login';
                    return Promise.reject(refreshError);
                } finally {
                    isRefreshing = false;
                }
            }
        }
        // Если запрос был сделан, но ответ не получен
        else if (error.request) {
            console.error('Error request:', error.request);
        }
        // Если произошла ошибка при настройке запроса
        else {
            console.error('Error message:', error.message);
        }

        return Promise.reject(error);
    }
);

export default api; 