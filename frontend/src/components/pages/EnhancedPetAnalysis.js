import React, { useState } from 'react';
import { Container, Row, Col, Card, Badge, ProgressBar, Alert, Modal, Button } from 'react-bootstrap';
import { FaCloudUploadAlt, FaBrain, FaChartLine, FaEye, FaPaw, FaHeart, FaSearch, FaPhone } from 'react-icons/fa';
import NavbarComp from './NavbarComp';
import api from '../../api/config';
import 'bootstrap/dist/css/bootstrap.min.css';
import '../../styles/common.css';
import '../../styles/EnhancedPetAnalysis.css';

const EnhancedPetAnalysis = () => {
  const [selectedFile, setSelectedFile] = useState(null);
  const [preview, setPreview] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [analysisResults, setAnalysisResults] = useState(null);
  const [similarPets, setSimilarPets] = useState([]);
  const [selectedPetDetails, setSelectedPetDetails] = useState(null);
  const [showDetailsModal, setShowDetailsModal] = useState(false);

  const translations = {
    // Типы животных
    'cat': 'Кошка',
    'dog': 'Собака',
    'bird': 'Птица',
    'rodent': 'Грызун',
    'rabbit': 'Кролик',
    'reptile': 'Рептилия',
    'other': 'Другое',
    'mixed': 'Смешанная порода',
    'domestic': 'Домашняя',
    'parrot': 'Попугай',
    'unknown': 'Неизвестно',

    // Цвета
    'black': 'Черный',
    'white': 'Белый',
    'gray': 'Серый',
    'light_gray': 'Светло-серый',
    'dark_gray': 'Темно-серый',
    'brown': 'Коричневый',
    'red': 'Рыжий',
    'dark_red': 'Темно-рыжий',
    'orange': 'Оранжевый',
    'yellow': 'Желтый',
    'golden': 'Золотистый',
    'green': 'Зеленый',
    'dark_green': 'Темно-зеленый',
    'blue': 'Голубой',
    'dark_blue': 'Темно-синий',
    'purple': 'Фиолетовый',
    'dark_purple': 'Темно-фиолетовый',
    'cyan': 'Бирюзовый',
    'teal': 'Сине-зеленый',
    'magenta': 'Пурпурный',
    'multicolor': 'Многоцветный',
    'spotted': 'Пятнистый',
    'striped': 'Полосатый',
    'tuxedo': 'Смокинг',
    'solid': 'Однотонный',
    'bicolor': 'Двухцветный',

    // Цвета глаз
    'amber': 'Янтарные',
    'hazel': 'Ореховые',
    'different': 'Разные (гетерохромия)',
    'turquoise': 'Бирюзовые',
    'dark_brown': 'Темно-коричневые',

    // Формы мордочки
    'round': 'Круглая',
    'oval': 'Овальная',
    'triangular': 'Треугольная',
    'long': 'Вытянутая',
    'flat': 'Плоская',
    'square': 'Квадратная',

    // Особые приметы
    'heterochromia': 'Гетерохромия (разные глаза)',
    'ear_fold': 'Залом на ухе',
    'eye_spot': 'Пятно на глазу',
    'tail_missing': 'Отсутствует хвост',
    'limb_missing': 'Отсутствует лапка',
    'albino': 'Альбинизм',
    'vitiligo': 'Витилиго',
    'spotted_pattern': 'Пятнистый узор',
    'striped_pattern': 'Полосатый узор',
    'fluffy_coat': 'Пушистая шерсть',
    'curly_coat': 'Кудрявая шерсть',
    'multiple': 'Несколько особенностей',
    'none': 'Отсутствуют',

    // Размеры
    'tiny': 'Очень маленький',
    'small': 'Маленький',
    'medium': 'Средний',
    'large': 'Большой',
    'extra_large': 'Очень большой'
  };

  const formatLabel = (label) => {
    if (!label) return 'неизвестно';
    return translations[label] || label;
  };

  const formatConfidence = (confidence) => {
    return `${Math.round((confidence || 0) * 100)}%`;
  };

  const getConfidenceColor = (confidence) => {
    if (confidence >= 0.8) return 'success';
    if (confidence >= 0.6) return 'warning';
    return 'danger';
  };

  const handleFileSelect = (event) => {
    const file = event.target.files[0];
    if (file) {
      if (file.size > 5 * 1024 * 1024) {
        setError('Размер файла не должен превышать 5MB');
        return;
      }
      setSelectedFile(file);
      setPreview(URL.createObjectURL(file));
      setError('');
      setAnalysisResults(null);
      setSimilarPets([]);
    }
  };

  const handleAnalyze = async () => {
    if (!selectedFile) {
      setError('Пожалуйста, выберите изображение');
      return;
    }

    // Валидация файла
    const maxSize = 10 * 1024 * 1024; // 10MB
    if (selectedFile.size > maxSize) {
      setError('Размер файла слишком большой. Максимальный размер: 10MB');
      return;
    }

    const allowedTypes = ['image/jpeg', 'image/jpg', 'image/png', 'image/gif'];
    if (!allowedTypes.includes(selectedFile.type)) {
      setError('Неподдерживаемый формат файла. Поддерживаются: JPEG, PNG, GIF');
      return;
    }

    setLoading(true);
    setError('');
    setAnalysisResults(null);
    setSimilarPets([]);

    try {
      // Проверяем доступность ML сервиса
      console.log('🔍 Проверяем доступность ML сервиса...');
      const healthResponse = await fetch('http://localhost:5004/', {
        method: 'GET',
        timeout: 5000
      });
      
      if (!healthResponse.ok) {
        throw new Error('ML сервис недоступен');
      }
      
      console.log('✅ ML сервис доступен');

      // Создаем FormData для отправки файла
      const formData = new FormData();
      formData.append('file', selectedFile); // Важно: имя поля должно быть 'file'

      const response = await fetch('http://localhost:5004/search/', {
        method: 'POST',
        body: formData
      });

      if (!response.ok) {
        const errorText = await response.text();
        throw new Error(`Ошибка при обработке изображения: ${errorText}`);
      }

      const data = await response.json();
      console.log('📦 Данные анализа получены:', data);
      console.log('🔍 Похожие питомцы:', data.similar_lost_pets);
      
      setAnalysisResults(data.analysis);
      setSimilarPets(data.similar_lost_pets || []);
      
    } catch (error) {
      console.error('💥 Ошибка при анализе:', error);
      setError(error.message || 'Произошла ошибка при анализе изображения');
    } finally {
      setLoading(false);
    }
  };

  const renderUniqueMetrics = () => {
    if (!analysisResults?.unique_metrics) return null;

    const metrics = analysisResults.unique_metrics;
    
    return (
      <Card className="mb-4">
        <Card.Header>
          <h5><FaChartLine className="me-2" />Уникальные метрики питомца</h5>
        </Card.Header>
        <Card.Body>
          <Row>
            <Col md={6}>
              <div className="metric-item mb-3">
                <label>Пушистость</label>
                <ProgressBar 
                  now={metrics.fluffiness * 100} 
                  label={`${Math.round(metrics.fluffiness * 100)}%`}
                  variant={metrics.fluffiness > 0.7 ? 'success' : metrics.fluffiness > 0.4 ? 'warning' : 'info'}
                />
                <small className="text-muted">
                  {metrics.fluffiness > 0.7 ? 'Очень пушистый' : 
                   metrics.fluffiness > 0.4 ? 'Умеренно пушистый' : 'Гладкошерстный'}
                </small>
              </div>
              
              <div className="metric-item mb-3">
                <label>Симметрия мордочки</label>
                <ProgressBar 
                  now={metrics.symmetry * 100} 
                  label={`${Math.round(metrics.symmetry * 100)}%`}
                  variant={metrics.symmetry > 0.8 ? 'success' : 'warning'}
                />
                <small className="text-muted">
                  {metrics.symmetry > 0.8 ? 'Очень симметричная' : 'Умеренно симметричная'}
                </small>
              </div>
            </Col>
            
            <Col md={6}>
              <div className="metric-item mb-3">
                <label>Сложность узора</label>
                <div className="d-flex align-items-center">
                  <Badge bg={metrics.pattern_complexity > 20 ? 'success' : metrics.pattern_complexity > 10 ? 'warning' : 'secondary'}>
                    {Math.round(metrics.pattern_complexity)}
                  </Badge>
                  <span className="ms-2">
                    {metrics.pattern_complexity > 20 ? 'Сложный узор' : 
                     metrics.pattern_complexity > 10 ? 'Умеренный узор' : 'Простой окрас'}
                  </span>
                </div>
              </div>
              
              <div className="metric-item mb-3">
                <label>Разнообразие цветов</label>
                <div className="d-flex align-items-center">
                  <Badge bg={metrics.color_diversity > 3 ? 'success' : metrics.color_diversity > 2 ? 'warning' : 'secondary'}>
                    {metrics.color_diversity}
                  </Badge>
                  <span className="ms-2">
                    {metrics.color_diversity > 3 ? 'Многоцветный' : 
                     metrics.color_diversity > 2 ? 'Двухцветный' : 'Однотонный'}
                  </span>
                </div>
              </div>
              
              <div className="metric-item mb-3">
                <label>Пропорции тела</label>
                <div className="d-flex align-items-center">
                  <Badge bg="info">
                    {metrics.body_proportions.toFixed(2)}
                  </Badge>
                  <span className="ms-2">
                    {metrics.body_proportions > 1.5 ? 'Вытянутое' : 
                     metrics.body_proportions < 0.8 ? 'Компактное' : 'Нормальное'}
                  </span>
                </div>
              </div>
            </Col>
          </Row>
        </Card.Body>
      </Card>
    );
  };

  const renderSimilarPets = () => {
    console.log('🐾 Rendering similar pets. Count:', similarPets.length);
    console.log('🐾 Similar pets data:', similarPets);
    
    if (similarPets.length === 0) {
      return (
        <Card>
          <Card.Header>
            <h5><FaHeart className="me-2" />Похожие питомцы</h5>
          </Card.Header>
          <Card.Body>
            <p className="text-muted">Похожие питомцы не найдены.</p>
          </Card.Body>
        </Card>
      );
    }

    return (
      <Card>
        <Card.Header>
          <h5><FaHeart className="me-2" />Похожие питомцы ({similarPets.length})</h5>
        </Card.Header>
        <Card.Body>
          <Row>
            {similarPets.map((pet, index) => (
              <Col md={6} lg={4} key={pet.id} className="mb-4">
                <Card className="h-100 pet-similarity-card">
                  <div className="position-relative">
                    <Card.Img 
                      variant="top" 
                      src={pet.image_url ? `http://localhost:8000/uploads/${pet.image_url}` : 'https://via.placeholder.com/300x200?text=Нет+фото'}
                      style={{ height: '200px', objectFit: 'cover' }}
                    />
                    <div className="similarity-overlay">
                      {pet.match_type === 'visual_similarity' ? (
                        <Badge bg="success" className="similarity-badge">
                          <FaEye className="me-1" />
                          {Math.round(pet.similarity * 100)}% визуальное сходство
                        </Badge>
                      ) : pet.match_type === 'breed_match' ? (
                        <Badge bg="primary" className="similarity-badge">
                          <FaPaw className="me-1" />
                          {Math.round(pet.similarity * 100)}% совпадение породы
                        </Badge>
                      ) : pet.match_type === 'color_match' ? (
                        <Badge bg="warning" className="similarity-badge">
                          <FaHeart className="me-1" />
                          {Math.round(pet.similarity * 100)}% совпадение цвета
                        </Badge>
                      ) : pet.match_type === 'type_match' ? (
                        <Badge bg="info" className="similarity-badge">
                          <FaPaw className="me-1" />
                          {Math.round(pet.similarity * 100)}% тип животного
                        </Badge>
                      ) : (
                        <Badge 
                          bg={pet.similarity >= 0.8 ? 'success' : pet.similarity >= 0.6 ? 'warning' : 'secondary'} 
                          className="similarity-badge"
                        >
                          <FaPaw className="me-1" />
                          {Math.round(pet.similarity * 100)}% сходство
                        </Badge>
                      )}
                    </div>
                  </div>
                  
                  <Card.Body>
                    <Card.Title className="h6">{pet.title}</Card.Title>
                    <div className="pet-details">
                      <small className="text-muted">
                        {formatLabel(pet.animal_type)} • {formatLabel(pet.color)}
                        {pet.breed && pet.breed !== 'Неопределена' && (
                          <> • {pet.breed}</>
                        )}
                      </small>
                    </div>
                    
                    {pet.ai_analyzed && (
                      <div className="mt-2">
                        <Badge bg="secondary" size="sm">
                          <FaBrain className="me-1" />
                          AI-анализ
                        </Badge>
                        {pet.ai_confidence && (
                          <Badge bg={getConfidenceColor(pet.ai_confidence)} size="sm" className="ms-1">
                            {formatConfidence(pet.ai_confidence)}
                          </Badge>
                        )}
                      </div>
                    )}
                    
                    <div className="mt-2">
                      <small className="text-muted">
                        {new Date(pet.created_at).toLocaleDateString('ru-RU')}
                      </small>
                    </div>
                  </Card.Body>
                  
                  <Card.Footer>
                    <button 
                      className="btn btn-outline-primary btn-sm w-100"
                      onClick={() => handleShowDetails(pet)}
                    >
                      Подробнее
                    </button>
                  </Card.Footer>
                </Card>
              </Col>
            ))}
          </Row>
        </Card.Body>
      </Card>
    );
  };

  // Функции для модального окна
  const handleShowDetails = (pet) => {
    setSelectedPetDetails(pet);
    setShowDetailsModal(true);
  };

  const handleCloseDetailsModal = () => {
    setShowDetailsModal(false);
    setSelectedPetDetails(null);
  };

  const formatDate = (dateString) => {
    if (!dateString) return 'неизвестно';
    return new Date(dateString).toLocaleDateString('ru-RU', {
      year: 'numeric',
      month: 'long',
      day: 'numeric'
    });
  };

  return (
    <>
      <NavbarComp />
      <div className="enhanced-analysis-container">
        <div className="analysis-header">
          <Container>
            <h1 className="analysis-title">
              <FaSearch className="me-3" />
              Поиск питомцев по фотографии
            </h1>
            <p className="analysis-description">
              Загрузите фотографию питомца для поиска похожих объявлений в базе данных
            </p>
          </Container>
        </div>

        <Container>
          <Row>
            <Col lg={4}>
              <Card className="upload-card mb-4">
                <Card.Header>
                  <h5>Загрузка изображения</h5>
                </Card.Header>
                <Card.Body>
                  <div 
                    className="upload-area"
                    onClick={() => document.getElementById('file-input').click()}
                  >
                    {preview ? (
                      <img src={preview} alt="Preview" className="image-preview" />
                    ) : (
                      <div className="upload-placeholder">
                        <FaCloudUploadAlt className="upload-icon" />
                        <p>Выберите фотографию</p>
                        <small>JPG, PNG до 5MB</small>
                      </div>
                    )}
                    <input
                      id="file-input"
                      type="file"
                      accept="image/*"
                      onChange={handleFileSelect}
                      style={{ display: 'none' }}
                    />
                  </div>
                  
                  <div className="analysis-controls">
                    <button 
                      className="analyze-button" 
                      onClick={handleAnalyze} 
                      disabled={!selectedFile || loading}
                    >
                      {loading ? 'Анализирую...' : 'Найти похожих питомцев'}
                    </button>
                  </div>
                </Card.Body>
              </Card>
            </Col>
            
            <Col lg={8}>
              {error && (
                <Alert variant="danger" className="mb-4">
                  {error}
                </Alert>
              )}

              {loading && (
                <Card className="mb-4">
                  <Card.Body className="text-center">
                    <div className="spinner-border text-primary mb-3" />
                    <h5>Выполняется поиск...</h5>
                    <p className="text-muted">
                      Анализируем изображение и ищем похожих питомцев в базе данных
                    </p>
                  </Card.Body>
                </Card>
              )}

              {renderUniqueMetrics()}
              {renderSimilarPets()}
            </Col>
          </Row>
        </Container>
      </div>

      {/* Модальное окно с подробной информацией */}
      <Modal show={showDetailsModal} onHide={handleCloseDetailsModal} size="lg">
        <Modal.Header closeButton>
          <Modal.Title>
            <FaHeart className="me-2 text-primary" />
            Подробная информация о питомце
          </Modal.Title>
        </Modal.Header>
        <Modal.Body>
          {selectedPetDetails && (
            <Row>
              <Col md={6}>
                <div className="text-center mb-3">
                  <img 
                    src={selectedPetDetails.image_url ? `http://localhost:8000/uploads/${selectedPetDetails.image_url}` : 'https://via.placeholder.com/400x300?text=Нет+фото'}
                    alt={selectedPetDetails.title}
                    className="img-fluid rounded"
                    style={{ maxHeight: '300px', objectFit: 'cover' }}
                  />
                </div>
                
                {/* Badges совпадения */}
                <div className="text-center mb-3">
                  {selectedPetDetails.match_type === 'visual_similarity' ? (
                    <Badge bg="success" className="p-2">
                      <FaEye className="me-1" />
                      {Math.round(selectedPetDetails.similarity * 100)}% визуальное сходство
                    </Badge>
                  ) : selectedPetDetails.match_type === 'breed_match' ? (
                    <Badge bg="primary" className="p-2">
                      <FaPaw className="me-1" />
                      {Math.round(selectedPetDetails.similarity * 100)}% совпадение породы
                    </Badge>
                  ) : selectedPetDetails.match_type === 'color_match' ? (
                    <Badge bg="warning" className="p-2">
                      <FaHeart className="me-1" />
                      {Math.round(selectedPetDetails.similarity * 100)}% совпадение цвета
                    </Badge>
                  ) : (
                    <Badge bg="info" className="p-2">
                      <FaPaw className="me-1" />
                      {Math.round(selectedPetDetails.similarity * 100)}% тип животного
                    </Badge>
                  )}
                </div>
              </Col>
              
              <Col md={6}>
                <h5 className="text-primary mb-3">{selectedPetDetails.title}</h5>
                
                <div className="mb-3">
                  <h6 className="text-muted mb-2">Описание:</h6>
                  <p className="text-justify">
                    {selectedPetDetails.description || 'Описание не указано'}
                  </p>
                </div>

                <Row className="mb-3">
                  <Col xs={6}>
                    <h6 className="text-muted mb-1">Тип животного:</h6>
                    <Badge bg="light" text="dark" className="p-2">
                      {formatLabel(selectedPetDetails.animal_type)}
                    </Badge>
                  </Col>
                  <Col xs={6}>
                    <h6 className="text-muted mb-1">Порода:</h6>
                    <Badge bg="light" text="dark" className="p-2">
                      {selectedPetDetails.breed || 'неизвестно'}
                    </Badge>
                  </Col>
                </Row>

                <Row className="mb-3">
                  <Col xs={6}>
                    <h6 className="text-muted mb-1">Цвет:</h6>
                    <Badge bg="light" text="dark" className="p-2">
                      {formatLabel(selectedPetDetails.color)}
                    </Badge>
                  </Col>
                  <Col xs={6}>
                    <h6 className="text-muted mb-1">Статус:</h6>
                    <Badge bg={selectedPetDetails.status === 'lost' ? 'danger' : 'success'} className="p-2">
                      {selectedPetDetails.status === 'lost' ? 'Потерян' : 'Найден'}
                    </Badge>
                  </Col>
                </Row>

                {/* Особенности */}
                {selectedPetDetails.features && selectedPetDetails.features.length > 0 && (
                  <div className="mb-3">
                    <h6 className="text-muted mb-2">Особенности:</h6>
                    <div>
                      {selectedPetDetails.features.map((feature, index) => (
                        <Badge key={index} bg="secondary" className="me-1 mb-1 p-2">
                          {formatLabel(feature)}
                        </Badge>
                      ))}
                    </div>
                  </div>
                )}

                <div className="mb-3">
                  <h6 className="text-muted mb-1">Дата потери:</h6>
                  <p className="mb-0">{formatDate(selectedPetDetails.lost_date)}</p>
                </div>

                {/* Контактная информация */}
                {selectedPetDetails.contact && (
                  <div className="mb-3">
                    <h6 className="text-muted mb-2">Контактная информация:</h6>
                    {selectedPetDetails.contact.name && (
                      <p className="mb-1">
                        <strong>Имя:</strong> {selectedPetDetails.contact.name}
                      </p>
                    )}
                    {selectedPetDetails.contact.phone && (
                      <p className="mb-1">
                        <strong>Телефон:</strong> 
                        <a href={`tel:${selectedPetDetails.contact.phone}`} className="ms-2 text-decoration-none">
                          {selectedPetDetails.contact.phone}
                        </a>
                      </p>
                    )}
                    {selectedPetDetails.contact.email && (
                      <p className="mb-1">
                        <strong>Email:</strong> 
                        <a href={`mailto:${selectedPetDetails.contact.email}`} className="ms-2 text-decoration-none">
                          {selectedPetDetails.contact.email}
                        </a>
                      </p>
                    )}
                  </div>
                )}

                {/* Местоположение */}
                {selectedPetDetails.lost_location && (
                  <div className="mb-3">
                    <h6 className="text-muted mb-2">Место потери:</h6>
                    <p className="mb-0">
                      {selectedPetDetails.lost_location.address || 'Адрес не указан'}
                    </p>
                    {selectedPetDetails.lost_location.latitude && selectedPetDetails.lost_location.longitude && (
                      <small className="text-muted">
                        Координаты: {selectedPetDetails.lost_location.latitude.toFixed(4)}, {selectedPetDetails.lost_location.longitude.toFixed(4)}
                      </small>
                    )}
                  </div>
                )}

                {/* Дата создания объявления */}
                <div className="text-muted">
                  <small>
                    Объявление создано: {formatDate(selectedPetDetails.created_at)}
                  </small>
                </div>
              </Col>
            </Row>
          )}
        </Modal.Body>
        <Modal.Footer>
          <Button variant="secondary" onClick={handleCloseDetailsModal}>
            Закрыть
          </Button>
          {selectedPetDetails?.contact?.phone && (
            <Button 
              variant="success" 
              href={`tel:${selectedPetDetails.contact.phone}`}
            >
              <FaPhone className="me-1" />
              Позвонить
            </Button>
          )}
        </Modal.Footer>
      </Modal>
    </>
  );
};

export default EnhancedPetAnalysis; 

