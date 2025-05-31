import React, { useState } from 'react';
import { Link } from 'react-router-dom';
import { Alert, Spinner } from 'react-bootstrap';
import api from '../../api/config';
import '../../styles/common.css';
import '../../styles/LoginPage.css';

export default function LoginPage() {
  const [formData, setFormData] = useState({
    username: '',
    password: ''
  });
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);

  const handleInputChange = (e) => {
    const { name, value } = e.target;
    setFormData(prev => ({
      ...prev,
      [name]: value
    }));
    setError('');
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError('');

    try {
      const response = await api.post('/api/token/', {
        username: formData.username,
        password: formData.password
      });

      if (!response.data || !response.data.access) {
        throw new Error('Не удалось получить токен доступа');
      }

      const token = response.data.access;
      const refreshToken = response.data.refresh;
      
      // Сохраняем оба токена
      localStorage.setItem('jwtToken', token);
      localStorage.setItem('refreshToken', refreshToken);
      
      api.defaults.headers.common['Authorization'] = `Bearer ${token}`;

      const userResponse = await api.get('/api/users/current/');
      
      if (!userResponse.data) {
        throw new Error('Не удалось получить информацию о пользователе');
      }

      const { id, username, email, profile } = userResponse.data;
      
      localStorage.setItem('currentUser', JSON.stringify({
        id,
        username,
        email,
        ...(profile || {})
      }));

      window.location.href = '/home';
    } catch (error) {
      console.error('Login error:', error);
      if (error.response) {
        if (error.response.status === 401) {
          setError('Неверное имя пользователя или пароль');
        } else {
          setError(error.response.data?.detail || 'Ошибка при входе в систему');
        }
      } else if (error.request) {
        setError('Не удалось подключиться к серверу');
      } else {
        setError('Произошла ошибка при входе в систему');
      }
    } finally {
      setLoading(false);
    }
  };

  const handleLoginError = (error) => {
    if (error.response) {
      switch (error.response.status) {
        case 401:
          setError('Неправильный логин или пароль. Пожалуйста, проверьте введенные данные.');
          break;
        case 400:
          setError('Пожалуйста, заполните все обязательные поля.');
          break;
        case 429:
          setError('Слишком много попыток входа. Пожалуйста, подождите несколько минут.');
          break;
        default:
          setError('Произошла ошибка при входе в систему. Пожалуйста, попробуйте позже.');
      }
    } else if (error.request) {
      setError('Не удалось подключиться к серверу. Пожалуйста, проверьте ваше интернет-соединение.');
    } else {
      setError('Что-то пошло не так. Пожалуйста, попробуйте еще раз или обратитесь в службу поддержки.');
    }
  };

  const fetchUserProfile = async () => {
    try {
      const response = await api.get('/api/users/current/');
      const { id, username, email, profile, pet_profile } = response.data;
      
      if (profile) {
        const { name, surname, phone, avatar } = profile;
        localStorage.setItem('currentUser', JSON.stringify({
          id,
          username,
          email,
          name,
          surname,
          phone,
          avatar
        }));
      }

      if (pet_profile) {
        const { type, sex, breed, color, photo, pet_name } = pet_profile;
        localStorage.setItem('currentPetUser', JSON.stringify({
          type,
          sex,
          breed,
          color,
          photo,
          pet_name
        }));
      }
    } catch (error) {
      console.error('Ошибка при загрузке профиля:', error);
    }
  };

  return (
    <div className="login-container">
      <div className="login-card">
        <h1 className="login-title">Вход в систему</h1>
        
        {error && <Alert variant="danger">{error}</Alert>}
        
        <form onSubmit={handleSubmit} className="login-form">
          <div className="form-group">
            <label className="form-label">Логин или email</label>
            <input
              type="text"
              name="username"
              className="form-control"
              value={formData.username}
              onChange={handleInputChange}
              placeholder="Введите ваш логин или email"
              required
              disabled={loading}
            />
          </div>

          <div className="form-group">
            <label className="form-label">Пароль</label>
            <input
              type="password"
              name="password"
              className="form-control"
              value={formData.password}
              onChange={handleInputChange}
              placeholder="Введите ваш пароль"
              required
              disabled={loading}
            />
          </div>

          <button
            type="submit"
            className="custom-button login-button"
            disabled={loading}
          >
            {loading ? (
              <>
                <Spinner
                  as="span"
                  animation="border"
                  size="sm"
                  role="status"
                  aria-hidden="true"
                  className="me-2"
                />
                Выполняется вход...
              </>
            ) : (
              'Войти'
            )}
          </button>
      </form>

        <div className="divider">
          <span>или</span>
        </div>

        <div className="login-footer">
          <p>Впервые у нас? <Link to="/register">Создайте аккаунт</Link></p>
          <p><Link to="/">На главную</Link></p>
        </div>
      </div>
    </div>
  );
}
