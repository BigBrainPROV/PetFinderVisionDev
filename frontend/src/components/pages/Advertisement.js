import React, { useState, useEffect } from 'react';
import { Container, Row, Col, Button } from 'react-bootstrap';
import { useParams, useHistory } from 'react-router-dom';
import { FaMapMarkerAlt, FaPhone, FaEnvelope, FaEdit, FaTrash } from 'react-icons/fa';
import NavbarComp from './NavbarComp';
import api from '../../api/config';
import '../../styles/common.css';
import '../../styles/Advertisement.css';

const Advertisement = () => {
  const [pet, setPet] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [currentUser, setCurrentUser] = useState(null);
  const { id } = useParams();
  const history = useHistory();

  useEffect(() => {
    const fetchData = async () => {
      try {
        setLoading(true);
        // Загружаем данные объявления
        const petResponse = await api.get(`/api/advertisements/${id}/`);
        setPet(petResponse.data);

        // Пытаемся получить текущего пользователя
        try {
          const userResponse = await api.get('/api/users/current/');
          setCurrentUser(userResponse.data);
        } catch (userError) {
          console.log('Пользователь не авторизован');
        }
      } catch (error) {
        console.error('Ошибка при загрузке данных:', error);
        if (error.response?.status === 401) {
          localStorage.removeItem('jwtToken');
          history.push('/login');
          return;
        }
        setError('Не удалось загрузить объявление');
      } finally {
        setLoading(false);
      }
    };

    fetchData();
  }, [id, history]);

  const handleEdit = () => {
    history.push(`/pet/${id}/edit`);
  };

  const handleDelete = async () => {
    if (window.confirm('Вы уверены, что хотите удалить это объявление?')) {
      try {
        await api.delete(`/api/advertisements/${id}/`);
        history.push('/');
      } catch (error) {
        console.error('Ошибка при удалении:', error);
        setError('Не удалось удалить объявление');
      }
    }
  };

  const formatDate = (dateString) => {
    const options = { year: 'numeric', month: 'long', day: 'numeric' };
    return new Date(dateString).toLocaleDateString('ru-RU', options);
  };

  if (loading) {
    return (
      <>
        <NavbarComp />
        <Container>
          <div className="loading-spinner">Загрузка...</div>
        </Container>
      </>
    );
  }

  if (error) {
    return (
      <>
        <NavbarComp />
        <Container>
          <div className="error-message">{error}</div>
        </Container>
      </>
    );
  }

  if (!pet) {
    return (
      <>
        <NavbarComp />
        <Container>
          <div className="error-message">Объявление не найдено</div>
        </Container>
      </>
    );
  }

  const isAuthor = currentUser && currentUser.username === pet.author;

  return (
    <>
      <NavbarComp />
      <Container className="advertisement-container">
        <Row>
          <Col md={8}>
            <div className="pet-details">
              <div className="pet-header">
                <h1>{pet.title}</h1>
                {isAuthor && (
                  <div className="author-actions">
                    <Button variant="outline-primary" onClick={handleEdit}>
                      <FaEdit /> Редактировать
                    </Button>
                    <Button variant="outline-danger" onClick={handleDelete}>
                      <FaTrash /> Удалить
                    </Button>
                  </div>
                )}
              </div>

              <div className="status-badge" data-status={pet.status}>
                {pet.status === 'lost' ? 'Потерян' : 'Найден'}
              </div>

              <div className="pet-photos">
                {pet.photos && pet.photos.length > 0 ? (
                  <img src={pet.photos[0]} alt={pet.title} className="main-photo" />
                ) : (
                  <div className="no-photo">Фото отсутствует</div>
                )}
              </div>

              <div className="pet-info">
                <h2>Информация о питомце</h2>
                <Row>
                  <Col md={6}>
                    <p><strong>Тип животного:</strong> {pet.type}</p>
                    <p><strong>Порода:</strong> {pet.breed || 'Не указана'}</p>
                    <p><strong>Пол:</strong> {
                      pet.sex === 'male' ? 'Мальчик' :
                      pet.sex === 'female' ? 'Девочка' :
                      'Неизвестно'
                    }</p>
                    <p><strong>Окрас:</strong> {pet.color}</p>
                  </Col>
                  <Col md={6}>
                    <p><strong>Цвет глаз:</strong> {pet.eye_color}</p>
                    <p><strong>Форма мордочки:</strong> {pet.face_shape}</p>
                    <p><strong>Особые приметы:</strong> {pet.special_features}</p>
                    <p><strong>Дата:</strong> {formatDate(pet.date)}</p>
                  </Col>
                </Row>
              </div>

              <div className="pet-description">
                <h2>Описание</h2>
                <p>{pet.description}</p>
              </div>
            </div>
          </Col>

          <Col md={4}>
            <div className="contact-info">
              <h2>Контактная информация</h2>
              <div className="contact-details">
                <p>
                  <strong>Контактное лицо:</strong><br />
                  {pet.contact_name}
                </p>
                {pet.phone && (
                  <p>
                    <FaPhone className="contact-icon" />
                    <a href={`tel:${pet.phone}`}>{pet.phone}</a>
                  </p>
                )}
                {pet.email && (
                  <p>
                    <FaEnvelope className="contact-icon" />
                    <a href={`mailto:${pet.email}`}>{pet.email}</a>
                  </p>
                )}
                {pet.location && (
                  <p>
                    <FaMapMarkerAlt className="contact-icon" />
                    {pet.location}
                  </p>
                )}
              </div>
            </div>
          </Col>
        </Row>
      </Container>
    </>
  );
};

export default Advertisement;