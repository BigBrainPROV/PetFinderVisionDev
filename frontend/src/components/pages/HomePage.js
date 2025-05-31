import React, { useEffect, useState } from 'react';
import { Container, Row, Col, Button, Form, Card } from 'react-bootstrap';
import { TransitionGroup, CSSTransition } from 'react-transition-group';
import { 
  FaSearch, 
  FaPaw, 
  FaHeart, 
  FaBell, 
  FaMapMarked, 
  FaUserFriends,
  FaShieldAlt,
  FaUser,
  FaClock
} from 'react-icons/fa';
import api from '../../api/config';
import NavbarComp from './NavbarComp';
import '../../styles/HomePage.css';

const HomePage = () => {
  const [reviews, setReviews] = useState([]);
  const [news, setNews] = useState([]);
  const [newReview, setNewReview] = useState({});
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchData = async () => {
      try {
        const [reviewsResponse, newsResponse] = await Promise.all([
          api.get('/api/feedback/'),
          api.get('/api/news/')
        ]);

        if (reviewsResponse.status === 200) {
          // Добавляем дату для отзывов, у которых её нет
          const reviewsWithDates = reviewsResponse.data.map(review => ({
            ...review,
            created_at: review.created_at || new Date().toISOString()
          }));
          console.log('Reviews with dates:', reviewsWithDates);
          setReviews(reviewsWithDates);
        }
        
        if (newsResponse.status === 200) {
          setNews(newsResponse.data);
        }
      } catch (error) {
        console.error('Error fetching data:', error);
      } finally {
        setLoading(false);
            }
    };

    fetchData();
  }, []);

  const handleInputChange = (event) => {
    const { name, value } = event.target;
    setNewReview((prevState) => ({ ...prevState, [name]: value }));
  };

  const handleSubmit = async (event) => {
    event.preventDefault();
    try {
      const currentDate = new Date().toISOString();
      const reviewData = {
        name: event.target.author.value,
        message: event.target.text.value,
        created_at: currentDate
      };
      
      const response = await api.post('/api/feedback/', reviewData);
      
      if (response.status === 201) {
        const newReview = {
          ...response.data,
          created_at: response.data.created_at || currentDate
        };
        setReviews(prevReviews => [...prevReviews, newReview]);
        setNewReview({});
        event.target.reset();
      }
    } catch (error) {
      console.error('Error submitting review:', error);
    }
  };

  const formatDate = (dateString) => {
    if (!dateString) {
      return 'Только что';
    }
    const date = new Date(dateString);
    if (isNaN(date.getTime())) {
      return 'Только что';
    }
    const options = { 
      year: 'numeric', 
      month: 'long', 
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    };
    return date.toLocaleDateString('ru-RU', options);
  };

  const features = [
    {
      icon: <FaSearch />,
      title: 'Умный поиск',
      description: 'Используйте современные технологии для поиска питомцев по характеристикам'
    },
    {
      icon: <FaPaw />,
      title: 'База данных питомцев',
      description: 'Большая база данных потерянных и найденных животных с подробной информацией'
    },
    {
      icon: <FaMapMarked />,
      title: 'Геолокация',
      description: 'Точный поиск по местоположению и отслеживание маршрутов передвижения'
    },
    {
      icon: <FaHeart />,
      title: 'Сообщество помощи',
      description: 'Активное сообщество неравнодушных людей, готовых помочь в поиске'
    },
    {
      icon: <FaBell />,
      title: 'Умные уведомления',
      description: 'Мгновенные оповещения о новых объявлениях и совпадениях в вашем районе'
    },
    {
      icon: <FaUserFriends />,
      title: 'Волонтерская сеть',
      description: 'Координация действий волонтеров и помощь в поиске питомцев'
    },
    {
      icon: <FaShieldAlt />,
      title: 'Защита данных',
      description: 'Безопасное хранение и обработка персональных данных пользователей'
    }
  ];

  if (loading) {
    return (
      <>
        <NavbarComp appName="PetFinderVision" />
        <div className="loading-container">
          <div className="spinner"></div>
        </div>
      </>
    );
  }

  return (
    <div className="home-page">
      <NavbarComp appName="PetFinderVision" />
      
      <div className="hero-section">
        <Container>
          <h1 className="hero-title">Найдите своего питомца</h1>
          <p className="hero-subtitle">
            Используйте современные технологии для поиска потерянных животных
          </p>
          <Button className="custom-button" size="lg" href="/search-by-post">
            Начать поиск
          </Button>
        </Container>
      </div>

      <section className="features-section">
        <Container>
          <h2 className="section-title">Наши возможности</h2>
          <Row className="justify-content-center">
            {features.map((feature, index) => (
              <Col key={index} xs={12} sm={6} md={4} lg={3} className="mb-4">
                <div className="feature-card">
                  <div className="feature-icon">{feature.icon}</div>
                  <h3>{feature.title}</h3>
                  <p>{feature.description}</p>
                </div>
              </Col>
            ))}
          </Row>
        </Container>
      </section>

      <Container>
        <Row className="mt-5">
          <Col md={6}>
            <h2 className="section-title">Последние новости</h2>
            <TransitionGroup>
              {news.map((item) => (
                <CSSTransition key={item.id} classNames="fade" timeout={300}>
                  <Card className="news-card">
                    <Card.Body>
                      <Card.Title>{item.title}</Card.Title>
                      <Card.Text>{item.description}</Card.Text>
                      <div className="news-date">
                        {new Date(item.created_at).toLocaleDateString('ru-RU')}
                      </div>
                    </Card.Body>
                  </Card>
                </CSSTransition>
              ))}
            </TransitionGroup>
          </Col>

          <Col md={6}>
            <h2 className="section-title">Отзывы</h2>
            <div className="review-form mb-4">
              <Form onSubmit={handleSubmit} className="review-form-container">
            <Form.Group controlId="author">
                  <Form.Label className="review-form-label">Ваше имя</Form.Label>
              <Form.Control
                type="text"
                name="author"
                    value={newReview.author || ''}
                onChange={handleInputChange}
                required
                    placeholder="Как вас зовут?"
                    className="review-input"
              />
            </Form.Group>
                <Form.Group controlId="text" className="mt-3">
                  <Form.Label className="review-form-label">Ваш отзыв</Form.Label>
              <Form.Control
                as="textarea"
                rows={3}
                name="text"
                    value={newReview.text || ''}
                onChange={handleInputChange}
                required
                    placeholder="Поделитесь своим опытом..."
                    className="review-input"
              />
            </Form.Group>
                <Button className="review-submit-button mt-3" type="submit">
                  Отправить отзыв
            </Button>
          </Form>
            </div>

            <TransitionGroup>
              {reviews.map((review) => (
                <CSSTransition key={review.id} classNames="fade" timeout={300}>
                    <Card className="review-card">
                      <Card.Body>
                      <div className="review-header">
                        <div className="review-user-info">
                          <div className="review-avatar">
                            {review.avatar ? (
                              <img src={review.avatar} alt={review.name} className="review-avatar-img" />
                            ) : (
                              <FaUser className="review-avatar-placeholder" />
                            )}
                          </div>
                          <div className="review-meta">
                            <h5 className="review-author">
                              <a href={`/profile/${review.user_id}`} className="review-author-link">
                                {review.name}
                              </a>
                            </h5>
                            <div className="review-date">
                              <FaClock className="review-date-icon" />
                              <span>{formatDate(review.created_at)}</span>
                            </div>
                          </div>
                        </div>
                      </div>
                      <div className="review-content">
                        <p className="review-text">{review.message}</p>
                        </div>
                  </Card.Body>
                </Card>
              </CSSTransition>
            ))}
          </TransitionGroup>
        </Col>
      </Row>
    </Container>
    </div>
  );
};

export default HomePage;
