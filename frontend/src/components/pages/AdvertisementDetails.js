import React, { useState, useEffect, useCallback } from 'react';
import { Container, Row, Col, Card, Button } from 'react-bootstrap';
import { useParams, useHistory } from 'react-router-dom';
import { FaPaw, FaMapMarkerAlt, FaPhone, FaEnvelope, FaUser } from 'react-icons/fa';
import NavbarComp from './NavbarComp';
import api from '../../api/config';
import '../../styles/common.css';
import '../../styles/AdvertisementDetails.css';

const AdvertisementDetails = () => {
  const [advertisement, setAdvertisement] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const { id } = useParams();
  const history = useHistory();

  const animalTypeLabels = {
    cat: 'Кошка',
    dog: 'Собака',
    bird: 'Птица',
    rodent: 'Грызун',
    rabbit: 'Кролик',
    reptile: 'Рептилия',
    other: 'Другое животное'
  };

  const colorLabels = {
    white: 'Белый',
    black: 'Черный',
    gray: 'Серый',
    brown: 'Коричневый',
    red: 'Рыжий',
    yellow: 'Желтый',
    green: 'Зеленый',
    blue: 'Голубой',
    multicolor: 'Многоцветный'
  };

  const sexLabels = {
    male: 'Мальчик',
    female: 'Девочка',
    unknown: 'Неизвестно'
  };

  const fetchAdvertisementDetails = useCallback(async () => {
    try {
      const response = await api.get(`/api/advertisements/${id}/`);
      setAdvertisement(response.data);
      setLoading(false);
    } catch (error) {
      console.error('Ошибка при загрузке объявления:', error);
      setError('Не удалось загрузить информацию об объявлении');
      setLoading(false);
    }
  }, [id]);

  useEffect(() => {
    fetchAdvertisementDetails();
  }, [fetchAdvertisementDetails]);

  const handleEdit = () => {
    history.push(`/post/${id}/edit`);
  };

  if (loading) {
    return (
      <>
        <NavbarComp />
        <div className="loading-container">
          <div className="spinner"></div>
          <p>Загрузка...</p>
        </div>
      </>
    );
  }

  if (error) {
    return (
      <>
        <NavbarComp />
        <Container>
          <div className="alert alert-danger mt-4">{error}</div>
        </Container>
      </>
    );
  }

  if (!advertisement) {
    return (
      <>
        <NavbarComp />
        <Container>
          <div className="alert alert-info mt-4">Объявление не найдено</div>
        </Container>
      </>
    );
  }

  return (
    <>
      <NavbarComp />
      <Container className="advertisement-details-container">
        <Card className="advertisement-details-card">
          <Row>
            <Col md={6}>
              <div className="main-photo-container">
                <img
                  src={advertisement.photo || 'https://via.placeholder.com/400x300?text=Нет+фото'}
                  alt="Фото питомца"
                  className="main-photo"
                />
                <div className={`status-badge status-${advertisement.status}`}>
                  {advertisement.status === 'lost' ? 'Потерян' : 'Найден'}
                </div>
              </div>
              {advertisement.additional_photos && advertisement.additional_photos.length > 0 && (
                <div className="additional-photos">
                  {advertisement.additional_photos.map((photo, index) => (
                    <img
                      key={index}
                      src={photo}
                      alt={`Дополнительное фото ${index + 1}`}
                      className="additional-photo"
                    />
                  ))}
                </div>
              )}
            </Col>
            <Col md={6}>
              <div className="advertisement-info">
                <h2>{advertisement.title}</h2>
                <div className="info-section">
                  <h4>Основная информация</h4>
                  <p><FaPaw /> Тип животного: {animalTypeLabels[advertisement.type] || advertisement.type}</p>
                  <p>Порода: {advertisement.breed}</p>
                  <p>Пол: {sexLabels[advertisement.sex] || advertisement.sex}</p>
                  <p>Цвет: {colorLabels[advertisement.color] || advertisement.color}</p>
                  <p>Цвет глаз: {advertisement.eye_color}</p>
                </div>

                <div className="info-section">
                  <h4>Описание</h4>
                  <p>{advertisement.description}</p>
                </div>

                <div className="info-section">
                  <h4>Местоположение</h4>
                  <p><FaMapMarkerAlt /> {advertisement.location}</p>
                </div>

                <div className="info-section">
                  <h4>Контактная информация</h4>
                  <p><FaUser /> {advertisement.contact_name || 'Не указано'}</p>
                  {advertisement.phone && <p><FaPhone /> {advertisement.phone}</p>}
                  {advertisement.email && <p><FaEnvelope /> {advertisement.email}</p>}
                </div>

                {localStorage.getItem('currentUser') && 
                 JSON.parse(localStorage.getItem('currentUser')).username === advertisement.author && (
                  <Button 
                    variant="primary" 
                    className="edit-button"
                    onClick={handleEdit}
                  >
                    Редактировать объявление
                  </Button>
                )}
              </div>
            </Col>
          </Row>
        </Card>
      </Container>
    </>
  );
};

export default AdvertisementDetails;

 