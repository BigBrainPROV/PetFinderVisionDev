import React, { useState, useEffect, useCallback } from 'react';
import { Container, Row, Col, Card, Button } from 'react-bootstrap';
import { Link, useHistory } from 'react-router-dom';
import { FaPaw, FaMapMarkerAlt } from 'react-icons/fa';
import NavbarComp from './NavbarComp';
import api from '../../api/config';
import '../../styles/common.css';
import '../../styles/MyAdvertisements.css';

const MyAdvertisements = () => {
  const [advertisements, setAdvertisements] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const history = useHistory();

  const fetchMyAdvertisements = useCallback(async () => {
    try {
      const response = await api.get('/api/advertisements/my_advertisements/');
      if (response.data) {
        const filteredAds = response.data.filter(ad => 
          ad.title !== "Temporary" && ad.description !== "Temporary"
        );
        setAdvertisements(filteredAds);
      }
    } catch (error) {
      console.error('Ошибка при загрузке объявлений:', error);
      
      if (error.response?.status === 401) {
        const refreshToken = localStorage.getItem('refreshToken');
        if (!refreshToken) {
          localStorage.removeItem('jwtToken');
          localStorage.removeItem('currentUser');
          history.push('/login');
          return;
        }
        
        try {
          const refreshResponse = await api.post('/api/token/refresh/', {
            refresh: refreshToken
          });
          
          if (refreshResponse.data.access) {
            const newToken = refreshResponse.data.access;
            localStorage.setItem('jwtToken', newToken);
            api.defaults.headers.common['Authorization'] = `Bearer ${newToken}`;
            
            const newResponse = await api.get('/api/advertisements/my_advertisements/');
            if (newResponse.data) {
              const filteredAds = newResponse.data.filter(ad => 
                ad.title !== "Temporary" && ad.description !== "Temporary"
              );
              setAdvertisements(filteredAds);
            }
          }
        } catch (refreshError) {
          localStorage.removeItem('jwtToken');
          localStorage.removeItem('refreshToken');
          localStorage.removeItem('currentUser');
          history.push('/login');
          return;
        }
      } else {
        setError('Не удалось загрузить объявления');
      }
    } finally {
      setLoading(false);
    }
  }, [history]);

  useEffect(() => {
    const token = localStorage.getItem('jwtToken');
    if (!token) {
      history.push('/login');
      return;
    }
    fetchMyAdvertisements();
  }, [history, fetchMyAdvertisements]);

  const getStatusLabel = (status) => {
    switch (status) {
      case 'lost':
        return 'Потерян';
      case 'found':
        return 'Найден';
      default:
        return status;
    }
  };

  const handleViewDetails = (adId) => {
    history.push(`/advertisement/${adId}`);
  };

  return (
    <div className="my-advertisements-container">
      <NavbarComp />
      <Container>
        <div className="my-advertisements-header">
          <h1 className="my-advertisements-title">Мои объявления</h1>
          <Link to="/post/new">
            <Button className="create-ad-button">
              <FaPaw /> Создать объявление
            </Button>
          </Link>
        </div>

        {error && <div className="alert alert-danger">{error}</div>}

        {loading ? (
          <div className="text-center">
            <div className="spinner-border text-primary" role="status">
              <span className="visually-hidden">Загрузка...</span>
            </div>
          </div>
        ) : (
          <Row xs={1} md={2} lg={3} className="g-4">
            {advertisements.length > 0 ? (
              advertisements.map((ad) => (
                <Col key={ad.id}>
                  <Card className="advertisement-card">
                    <div className="card-image-container">
                      <Card.Img
                        variant="top"
                        src={ad.photo || 'https://via.placeholder.com/300x200?text=Нет+фото'}
                        className="card-image"
                      />
                      <div className={`status-badge status-${ad.status}`}>
                        {getStatusLabel(ad.status)}
                      </div>
                    </div>
                    <Card.Body>
                      <Card.Title>{ad.title}</Card.Title>
                      <Card.Text className="description">
                        {ad.description}
                      </Card.Text>
                      <div className="pet-info">
                        <span className="pet-type">
                          <FaPaw /> {ad.type}
                        </span>
                        {ad.location && (
                          <span className="location">
                            <FaMapMarkerAlt /> {ad.location}
                          </span>
                        )}
                      </div>
                      <Button 
                        variant="outline-primary" 
                        className="w-100"
                        onClick={() => handleViewDetails(ad.id)}
                      >
                        Подробнее
                      </Button>
                    </Card.Body>
                  </Card>
                </Col>
              ))
            ) : (
              <Col xs={12}>
                <div className="no-advertisements">
                  <FaPaw className="no-ads-icon" />
                  <h3>У вас пока нет объявлений</h3>
                  <p>Создайте новое объявление о пропаже или находке питомца</p>
                  <Link to="/post/new">
                    <Button className="create-first-ad-button">
                      <FaPaw /> Создать объявление
                    </Button>
                  </Link>
                </div>
              </Col>
            )}
          </Row>
        )}
      </Container>
    </div>
  );
};

export default MyAdvertisements; 