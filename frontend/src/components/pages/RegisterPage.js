import React, { useState } from 'react';
import { Link } from 'react-router-dom';
import { Alert, Spinner } from 'react-bootstrap';
import { FaCheck, FaTimes } from 'react-icons/fa';
import api from '../../api/config';
import '../../styles/common.css';
import '../../styles/RegisterPage.css';

export default function RegisterPage() {
  const [formData, setFormData] = useState({
    username: '',
    email: '',
    password: '',
    confirmPassword: '',
    acceptTerms: false
  });
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);

  const passwordRequirements = [
    { text: 'Минимум 8 символов', test: pwd => pwd.length >= 8 },
    { text: 'Хотя бы одна заглавная буква', test: pwd => /[A-Z]/.test(pwd) },
    { text: 'Хотя бы одна цифра', test: pwd => /[0-9]/.test(pwd) },
    { text: 'Хотя бы один специальный символ', test: pwd => /[!@#$%^&*]/.test(pwd) }
  ];

  const handleInputChange = (e) => {
    const { name, value, type, checked } = e.target;
    setFormData(prev => ({
      ...prev,
      [name]: type === 'checkbox' ? checked : value
    }));
    setError('');
  };

  const validateForm = () => {
    if (!formData.username || !formData.email || !formData.password || !formData.confirmPassword) {
      setError('Пожалуйста, заполните все обязательные поля.');
      return false;
    }

    if (!formData.email.match(/^[^\s@]+@[^\s@]+\.[^\s@]+$/)) {
      setError('Пожалуйста, введите корректный email адрес.');
      return false;
    }

    if (formData.password !== formData.confirmPassword) {
      setError('Пароли не совпадают.');
      return false;
    }

    if (!passwordRequirements.every(req => req.test(formData.password))) {
      setError('Пароль не соответствует требованиям безопасности.');
      return false;
    }

    if (!formData.acceptTerms) {
      setError('Пожалуйста, примите условия использования.');
      return false;
    }

    return true;
  };

  const handleSubmit = async (e) => {
    e.preventDefault();

    if (!validateForm()) {
      return;
    }

    setLoading(true);
    setError('');

    try {
      const response = await api.post('/api/users/', {
        username: formData.username,
        email: formData.email,
        password: formData.password
      });

      if (response.status === 201) {
        // Автоматический вход после регистрации
        const loginResponse = await api.post('/api/token/', {
          username: formData.username,
          password: formData.password
        });

        const token = loginResponse.data.access;
        const refreshToken = loginResponse.data.refresh;
        
        // Сохраняем оба токена
        localStorage.setItem('jwtToken', token);
        localStorage.setItem('refreshToken', refreshToken);
        
        api.defaults.headers.common['Authorization'] = `Bearer ${token}`;

        window.location.href = '/home';
      }
    } catch (error) {
      if (error.response) {
        if (error.response.status === 400) {
          const errors = error.response.data;
          if (errors.username) {
            setError('Это имя пользователя уже занято.');
          } else if (errors.email) {
            setError('Этот email уже используется.');
          } else {
            setError('Пожалуйста, проверьте правильность заполнения всех полей.');
          }
        } else {
          setError('Произошла ошибка при регистрации. Пожалуйста, попробуйте позже.');
        }
      } else if (error.request) {
        setError('Не удалось подключиться к серверу. Пожалуйста, проверьте ваше интернет-соединение.');
      } else {
        setError('Что-то пошло не так. Пожалуйста, попробуйте еще раз или обратитесь в службу поддержки.');
      }
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="register-container">
      <div className="register-card">
        <h1 className="register-title">Регистрация</h1>
        
        {error && <Alert variant="danger">{error}</Alert>}
        
        <form onSubmit={handleSubmit} className="register-form">
          <div className="form-group">
            <label className="form-label">Имя пользователя</label>
          <input
            type="text"
            name="username"
              className="form-control"
              value={formData.username}
              onChange={handleInputChange}
              placeholder="Придумайте имя пользователя"
            required
              disabled={loading}
          />
          </div>

          <div className="form-group">
            <label className="form-label">Email</label>
          <input
            type="email"
            name="email"
              className="form-control"
              value={formData.email}
              onChange={handleInputChange}
              placeholder="Введите ваш email"
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
              placeholder="Придумайте пароль"
              required
              disabled={loading}
            />
            <div className="password-requirements">
              {passwordRequirements.map((req, index) => (
                <div key={index} className="requirement-item">
                  {req.test(formData.password) ? (
                    <FaCheck className="requirement-icon" />
                  ) : (
                    <FaTimes className="requirement-icon invalid" />
                  )}
                  {req.text}
                </div>
              ))}
            </div>
          </div>

          <div className="form-group">
            <label className="form-label">Подтверждение пароля</label>
            <input
              type="password"
              name="confirmPassword"
              className="form-control"
              value={formData.confirmPassword}
              onChange={handleInputChange}
              placeholder="Повторите пароль"
            required
              disabled={loading}
            />
          </div>

          <div className="terms-checkbox">
            <input
              type="checkbox"
              name="acceptTerms"
              id="acceptTerms"
              checked={formData.acceptTerms}
              onChange={handleInputChange}
              disabled={loading}
            />
            <label htmlFor="acceptTerms" className="terms-label">
              Я принимаю условия использования и политику конфиденциальности
            </label>
          </div>

          <button
            type="submit"
            className="custom-button register-button"
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
                Регистрация...
              </>
            ) : (
              'Зарегистрироваться'
            )}
          </button>
      </form>

        <div className="register-footer">
          <p>Уже есть аккаунт? <Link to="/login">Войдите</Link></p>
          <p><Link to="/">На главную</Link></p>
        </div>
      </div>
    </div>
  );
}

