import React, { useState, useEffect, useRef } from 'react';
import { Container, Form, Button, Image } from 'react-bootstrap';
import { withRouter } from 'react-router-dom';
import { FaCamera, FaEdit, FaSave, FaTimes, FaPaw } from 'react-icons/fa';
import NavbarComp from './NavbarComp';
import api from '../../api/config';
import '../../styles/common.css';
import '../../styles/ProfilePage.css';

const ProfilePage = ({ history }) => {
  const [profile, setProfile] = useState({
    name: '',
    surname: '',
    phone: '',
    avatar: null,
  });
  const [isEditMode, setIsEditMode] = useState(false);
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);
  const [isHovered, setIsHovered] = useState(false);
  const fileInputRef = useRef(null);
  const [success, setSuccess] = useState('');

  useEffect(() => {
    const token = localStorage.getItem('jwtToken');
    if (!token) {
      history.push('/login');
      return;
    }

    const storedProfile = localStorage.getItem('currentUser');
    if (storedProfile) {
      try {
        const parsedProfile = JSON.parse(storedProfile);
        setProfile(parsedProfile);
      } catch (e) {
        console.error('Ошибка при парсинге профиля:', e);
        setError('Ошибка при загрузке профиля');
      }
    }
  }, [history]);

  const handleInputChange = (event) => {
    const { name, value } = event.target;
    setProfile(prev => ({ ...prev, [name]: value }));
    setError('');
  };

  const handleAvatarClick = () => {
    if (fileInputRef.current) {
      fileInputRef.current.click();
    }
  };

  const handleFileChange = async (event) => {
    const file = event.target.files?.[0];
    if (file) {
      if (file.size > 5 * 1024 * 1024) {
        setError('Размер файла не должен превышать 5MB');
        return;
      }
      if (!file.type.startsWith('image/')) {
        setError('Пожалуйста, выберите изображение');
        return;
      }

      try {
        setLoading(true);
    const formData = new FormData();
        formData.append('file', file);

        const response = await api.post('/api/users/avatar/', formData, {
      headers: {
            'Content-Type': 'multipart/form-data',
      },
        });

        if (response.status === 204) {
          // Получаем обновленные данные профиля
          const profileResponse = await api.get('/api/users/current/');
          const { avatar } = profileResponse.data.profile;
          
          setProfile(prev => ({
            ...prev,
            avatar
          }));

          const currentUser = JSON.parse(localStorage.getItem('currentUser') || '{}');
          localStorage.setItem('currentUser', JSON.stringify({
            ...currentUser,
            avatar
          }));
          
          setSuccess('Аватар успешно обновлен');
          setTimeout(() => setSuccess(''), 3000);
        }
      } catch (error) {
        console.error('Ошибка при загрузке аватара:', error);
        if (error.response?.data) {
          setError(error.response.data.detail || 'Ошибка при загрузке аватара');
        } else {
          setError('Ошибка при загрузке аватара');
        }
      } finally {
        setLoading(false);
      }
    }
  };

  const handleSave = async () => {
    try {
      setLoading(true);
      const response = await api.post('/api/users/current/', {
        profile: {
          name: profile.name,
      surname: profile.surname,
      phone: profile.phone
        }
      });

      if (response.status === 200 || response.status === 201) {
        const currentUser = JSON.parse(localStorage.getItem('currentUser') || '{}');
        localStorage.setItem('currentUser', JSON.stringify({
          ...currentUser,
          ...profile,
          ...response.data.profile
        }));
        setIsEditMode(false);
        setError('');
        setSuccess('Профиль успешно обновлен');
        setTimeout(() => setSuccess(''), 3000);
      }
    } catch (error) {
      console.error('Ошибка при сохранении профиля:', error);
      if (error.response?.data) {
        setError(error.response.data.detail || 'Ошибка при сохранении данных');
      } else {
        setError('Ошибка при сохранении данных');
      }
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="profile-container">
      <NavbarComp />
      <Container>
        <div className="profile-card">
          <h1 className="profile-title">Мой профиль</h1>

          <div className="avatar-section">
            <div 
              className="avatar-container"
              onMouseEnter={() => setIsHovered(true)}
              onMouseLeave={() => setIsHovered(false)}
              onClick={handleAvatarClick}
            >
              <Image
                src={profile.avatar || 'https://via.placeholder.com/150?text=Аватар'}
                alt="Аватар профиля"
                className="profile-avatar"
                roundedCircle
              />
              {isHovered && (
                <div className="avatar-overlay">
                  <FaCamera className="camera-icon" />
                </div>
              )}
              <input
                type="file"
                ref={fileInputRef}
                onChange={handleFileChange}
                accept="image/*"
                style={{ display: 'none' }}
              />
            </div>
          </div>

          {error && <div className="alert alert-danger">{error}</div>}
          {success && <div className="alert alert-success">{success}</div>}

          <Form>
            <Form.Group className="mb-3">
                <Form.Label>Фамилия</Form.Label>
                <Form.Control
                  type="text"
                  name="surname"
                  value={profile.surname || ''}
                  onChange={handleInputChange}
                  disabled={!isEditMode}
                placeholder="Введите фамилию"
                />
              </Form.Group>

            <Form.Group className="mb-3">
                <Form.Label>Имя</Form.Label>
                <Form.Control
                  type="text"
                  name="name"
                  value={profile.name || ''}
                  onChange={handleInputChange}
                  disabled={!isEditMode}
                placeholder="Введите имя"
                />
              </Form.Group>

            <Form.Group className="mb-3">
                <Form.Label>Номер телефона</Form.Label>
                <Form.Control
                type="tel"
                  name="phone"
                  value={profile.phone || ''}
                  onChange={handleInputChange}
                  disabled={!isEditMode}
                placeholder="+7 (XXX) XXX-XX-XX"
                />
              </Form.Group>

            <div className="button-group">
              {!isEditMode ? (
                <Button 
                  className="edit-button"
                  onClick={() => setIsEditMode(true)}
                  disabled={loading}
                >
                  <FaEdit />
                  Редактировать
                </Button>
              ) : (
                <>
                  <Button 
                    className="save-button"
                    onClick={handleSave}
                    disabled={loading}
                  >
                    <FaSave />
                    {loading ? 'Сохранение...' : 'Сохранить'}
                  </Button>
                  <Button 
                    className="cancel-button"
                    onClick={() => setIsEditMode(false)}
                    disabled={loading}
                  >
                    <FaTimes />
                    Отмена
                  </Button>
                </>
              )}
              <Button 
                className="my-ads-button"
                onClick={() => history.push('/post/new')}
                disabled={loading}
              >
                <FaPaw />
                Создать объявление
              </Button>
              <Button 
                className="my-ads-button"
                onClick={() => history.push('/my-advertisements')}
                disabled={loading}
              >
                <FaPaw />
                Мои объявления
              </Button>
            </div>
            </Form>
        </div>
      </Container>
    </div>
  );
};

export default withRouter(ProfilePage);