import React, { useState, useEffect, useRef, useCallback } from 'react';
import { Container, Form, Button, Card, Row, Col, Modal, Spinner, Alert } from 'react-bootstrap';
import { YMaps, Map, Placemark, SearchControl, ZoomControl } from '@pbe/react-yandex-maps';
import { FaPaw, FaMapMarkerAlt, FaFilter, FaSearch } from 'react-icons/fa';
import NavbarComp from './NavbarComp';
import api from '../../api/config';
import { YANDEX_MAPS_API_KEY, DEFAULT_CENTER, DEFAULT_ZOOM } from '../../config';
import '../../styles/SearchByLocation.css';

const SearchByLocation = () => {
  const [advertisements, setAdvertisements] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [selectedType, setSelectedType] = useState('all');
  const [showFilters, setShowFilters] = useState(false);
  const [mapCenter, setMapCenter] = useState(DEFAULT_CENTER);
  const [selectedAd, setSelectedAd] = useState(null);
  const [mapRef, setMapRef] = useState(null);
  const [showModal, setShowModal] = useState(false);
  const [newMarkerPosition, setNewMarkerPosition] = useState(null);
  const [showNewMarkerModal, setShowNewMarkerModal] = useState(false);
  const [newMarkerData, setNewMarkerData] = useState({
    title: '',
    description: '',
    type: 'cat',
    status: 'lost',
    breed: '',
    color: 'white',
    sex: 'unknown',
    eye_color: 'yellow',
    face_shape: 'round',
    special_features: 'none',
    photo: null,
    phone: '',
    social_media: ''
  });
  const [photoPreview, setPhotoPreview] = useState(null);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const fileInputRef = useRef(null);
  const [breeds, setBreeds] = useState([]);

  const animalTypes = [
    { value: 'cat', label: 'Кошка' },
    { value: 'dog', label: 'Собака' },
    { value: 'bird', label: 'Птица' },
    { value: 'rodent', label: 'Грызун' },
    { value: 'rabbit', label: 'Кролик' },
    { value: 'reptile', label: 'Рептилия' },
    { value: 'other', label: 'Другое' }
  ];

  const colorOptions = [
    { value: 'white', label: 'Белый' },
    { value: 'black', label: 'Черный' },
    { value: 'gray', label: 'Серый' },
    { value: 'brown', label: 'Коричневый' },
    { value: 'red', label: 'Рыжий' },
    { value: 'yellow', label: 'Желтый' },
    { value: 'green', label: 'Зеленый' },
    { value: 'blue', label: 'Голубой' },
    { value: 'multicolor', label: 'Многоцветный' }
  ];

  const sexOptions = [
    { value: 'male', label: 'Мальчик' },
    { value: 'female', label: 'Девочка' },
    { value: 'unknown', label: 'Неизвестно' }
  ];

  const eyeColorOptions = [
    { value: 'blue', label: 'Голубые' },
    { value: 'green', label: 'Зеленые' },
    { value: 'yellow', label: 'Желтые' },
    { value: 'brown', label: 'Карие' },
    { value: 'black', label: 'Черные' },
    { value: 'red', label: 'Красные' },
    { value: 'different', label: 'Разные' }
  ];

  const faceShapeOptions = [
    { value: 'round', label: 'Круглая' },
    { value: 'oval', label: 'Овальная' },
    { value: 'triangular', label: 'Треугольная' },
    { value: 'long', label: 'Вытянутая' },
    { value: 'flat', label: 'Плоская' },
    { value: 'other', label: 'Другая' }
  ];

  const specialFeaturesOptions = [
    { value: 'heterochromia', label: 'Гетерохромия' },
    { value: 'ear_fold', label: 'Залом на ухе' },
    { value: 'eye_spot', label: 'Пятно на глазу' },
    { value: 'tail_missing', label: 'Отсутствует хвост' },
    { value: 'limb_missing', label: 'Отсутствует лапка' },
    { value: 'albino', label: 'Альбинизм' },
    { value: 'vitiligo', label: 'Витилиго' },
    { value: 'none', label: 'Нет особых примет' }
  ];

  const handleTypeChange = (event) => {
    setSelectedType(event.target.value);
  };

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

  const getTypeLabel = (type) => {
    const foundType = animalTypes.find(t => t.value === type);
    return foundType ? foundType.label : type;
  };

  const getColorLabel = (color) => {
    const foundColor = colorOptions.find(c => c.value === color);
    return foundColor ? foundColor.label : color;
  };

  const getSexLabel = (sex) => {
    const foundSex = sexOptions.find(s => s.value === sex);
    return foundSex ? foundSex.label : sex;
  };

  const getEyeColorLabel = (eyeColor) => {
    const foundEyeColor = eyeColorOptions.find(ec => ec.value === eyeColor);
    return foundEyeColor ? foundEyeColor.label : eyeColor;
  };

  const getFaceShapeLabel = (faceShape) => {
    const foundFaceShape = faceShapeOptions.find(fs => fs.value === faceShape);
    return foundFaceShape ? foundFaceShape.label : faceShape;
  };

  const getSpecialFeaturesLabel = (features) => {
    const foundFeatures = specialFeaturesOptions.find(sf => sf.value === features);
    return foundFeatures ? foundFeatures.label : features;
  };

  const handlePlacemarkClick = (ad) => {
    console.log('Данные объявления при клике:', ad);
    setSelectedAd({
      ...ad,
      color: ad.color || 'white',
      sex: ad.sex || 'unknown',
      eye_color: ad.eye_color || 'yellow',
      face_shape: ad.face_shape || 'round',
      special_features: ad.special_features || 'none'
    });
    if (mapRef) {
      mapRef.setCenter([ad.latitude, ad.longitude]);
    }
  };

  const handleShowDetails = (ad) => {
    console.log('Данные объявления при показе деталей:', ad);
    setSelectedAd({
      ...ad,
      color: ad.color || 'white',
      sex: ad.sex || 'unknown',
      eye_color: ad.eye_color || 'yellow',
      face_shape: ad.face_shape || 'round',
      special_features: ad.special_features || 'none'
    });
    setShowModal(true);
    if (mapRef && ad.latitude && ad.longitude) {
      mapRef.setCenter([ad.latitude, ad.longitude]);
    }
  };

  const mapState = {
    center: mapCenter,
    zoom: DEFAULT_ZOOM,
    controls: []
  };

  const handleMapClick = (e) => {
    const coords = e.get('coords');
    setNewMarkerPosition(coords);
    setShowNewMarkerModal(true);
  };

  const handlePhotoChange = (e) => {
    const file = e.target.files[0];
    if (file) {
      setNewMarkerData({ ...newMarkerData, photo: file });
      const reader = new FileReader();
      reader.onloadend = () => {
        setPhotoPreview(reader.result);
      };
      reader.readAsDataURL(file);
    }
  };

  const handleMarkerDrag = (e) => {
    const coords = e.get('target').geometry.getCoordinates();
    setNewMarkerPosition(coords);
  };

  const handleCreateNewMarker = async () => {
    try {
      setIsSubmitting(true);
      const [latitude, longitude] = newMarkerPosition;

      // Создаем объект с данными
      const markerData = {
        title: newMarkerData.status === 'lost' ? 'Потерян питомец' : 'Найден питомец',
        description: newMarkerData.description,
        type: newMarkerData.type,
        status: newMarkerData.status,
        breed: newMarkerData.breed,
        color: newMarkerData.color || 'white',
        sex: newMarkerData.sex || 'unknown',
        eye_color: newMarkerData.eye_color || 'yellow',
        face_shape: newMarkerData.face_shape || 'round',
        special_features: newMarkerData.special_features || 'none',
        phone: newMarkerData.phone,
        social_media: newMarkerData.social_media,
        latitude: latitude.toString(),
        longitude: longitude.toString(),
        location: 'Определяется...',
        author: localStorage.getItem('username') || 'Аноним'
      };

      console.log('Отправляемые данные:', markerData);

      const formData = new FormData();
      
      // Добавляем все поля в formData
      for (const [key, value] of Object.entries(markerData)) {
        if (value !== undefined && value !== null) {
          formData.append(key, value);
        }
      }

      // Добавляем фото отдельно, если оно есть
      if (newMarkerData.photo) {
        formData.append('photo', newMarkerData.photo);
      }

      // Логируем содержимое FormData перед отправкой
      for (let pair of formData.entries()) {
        console.log(pair[0] + ': ' + pair[1]);
      }

      const response = await api.post('/api/advertisements/', formData, {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
      });

      console.log('Ответ сервера:', response.data);

      // Преобразуем полученные данные
      const newAd = {
        ...response.data,
        color: response.data.color || 'white',
        sex: response.data.sex || 'unknown',
        eye_color: response.data.eye_color || 'yellow',
        face_shape: response.data.face_shape || 'round',
        special_features: response.data.special_features || 'none'
      };

      // Обновляем список объявлений
      setAdvertisements(prevAds => [...prevAds, newAd]);
      
      // Очищаем форму
      setShowNewMarkerModal(false);
      setNewMarkerPosition(null);
      setPhotoPreview(null);
      setNewMarkerData({
        title: '',
        description: '',
        type: 'cat',
        status: 'lost',
        breed: '',
        color: 'white',
        sex: 'unknown',
        eye_color: 'yellow',
        face_shape: 'round',
        special_features: 'none',
        photo: null,
        phone: '',
        social_media: ''
      });

      // Показываем сообщение об успехе
      alert('Объявление успешно создано!');

      // Обновляем список объявлений
      await fetchAdvertisements();

    } catch (error) {
      console.error('Подробная информация об ошибке:', error);
      let errorMessage = 'Произошла ошибка при создании объявления: ';
      
      if (error.response?.data) {
        if (typeof error.response.data === 'object') {
          Object.entries(error.response.data).forEach(([key, value]) => {
            errorMessage += `\n${key}: ${value}`;
          });
        } else {
          errorMessage += error.response.data;
        }
      } else {
        errorMessage += error.message || 'Неизвестная ошибка';
      }
      
      alert(errorMessage);
    } finally {
      setIsSubmitting(false);
    }
  };

  const handleMapLoad = (ymaps) => {
    if (ymaps) {
      setMapRef(ymaps);
    }
  };

  const loadBreeds = async (animalType) => {
    try {
      const response = await api.get(`/api/users/breeds/?type=${animalType}`);
      setBreeds(response.data);
    } catch (error) {
      console.error('Ошибка при загрузке пород:', error);
      setBreeds([]);
    }
  };

  useEffect(() => {
    if (newMarkerData.type) {
      loadBreeds(newMarkerData.type);
    }
  }, [newMarkerData.type]);

  const setMapToEkaterinburg = useCallback(() => {
    // Устанавливаем центр карты на Екатеринбург
    const ekaterinburgCenter = [56.8431, 60.6454];
    setMapCenter(ekaterinburgCenter);
    if (mapRef) {
      mapRef.setCenter(ekaterinburgCenter);
    }
  }, [mapRef]);

  const fetchAdvertisements = useCallback(async () => {
    try {
      setLoading(true);
      const response = await api.get('/api/advertisements/', {
        params: {
          type: selectedType !== 'all' ? selectedType : undefined
        }
      });
      console.log('Полученные объявления:', response.data);
      
      // Добавляем значения по умолчанию для каждого объявления
      const processedAds = response.data.map(ad => ({
        ...ad,
        color: ad.color || 'white',
        sex: ad.sex || 'unknown',
        eye_color: ad.eye_color || 'yellow',
        face_shape: ad.face_shape || 'round',
        special_features: ad.special_features || 'none'
      }));
      
      setAdvertisements(processedAds);
    } catch (error) {
      console.error('Ошибка при загрузке объявлений:', error);
      setError('Не удалось загрузить объявления');
    } finally {
      setLoading(false);
    }
  }, [selectedType]);

  useEffect(() => {
    fetchAdvertisements();
  }, [fetchAdvertisements]);

  useEffect(() => {
    setMapToEkaterinburg();
  }, [setMapToEkaterinburg]);

  return (
    <div className="search-location-container">
      <NavbarComp />
      
      {/* Добавляем баннер */}
      <div className="location-banner">
        <h1>Поиск по геопозиции</h1>
        <p>Найдите потерянных или найденных питомцев рядом с вами на карте</p>
      </div>

      {loading && (
        <div className="loading-overlay">
          <Spinner animation="border" role="status">
            <span className="visually-hidden">Загрузка...</span>
          </Spinner>
        </div>
      )}
      {error && (
        <div className="alert alert-danger" role="alert">
          {error}
        </div>
      )}
      <Container fluid>
        <Row>
          <Col md={3} className="filters-sidebar">
            <div className="filters-header">
              <h2>Фильтры</h2>
              <Button 
                variant="link" 
                className="toggle-filters-btn"
                onClick={() => setShowFilters(!showFilters)}
              >
                <FaFilter />
              </Button>
          </div>

            <div className={`filters-content ${showFilters ? 'show' : ''}`}>
              {/* Фильтр по типу животного */}
              <Form.Group>
                <Form.Label>Тип животного</Form.Label>
                <Form.Control
                  as="select"
                  value={selectedType}
                  onChange={handleTypeChange}
                >
                  <option value="all">Все животные</option>
                  {animalTypes.map(type => (
                    <option key={type.value} value={type.value}>
                      {type.label}
                    </option>
                  ))}
                </Form.Control>
              </Form.Group>

              {/* Кнопка обновления поиска */}
              <Button
                variant="outline-primary"
                className="w-100 mt-3"
                onClick={() => fetchAdvertisements()}
                disabled={loading}
              >
                <FaSearch className="me-2" />
                {loading ? 'Поиск...' : 'Обновить поиск'}
              </Button>

              {advertisements.length > 0 && (
                <div className="advertisement-list">
                  {advertisements.map(ad => (
                    <Card 
                      key={ad.id} 
                      className={`advertisement-card ${selectedAd?.id === ad.id ? 'selected' : ''}`}
                      onClick={() => handlePlacemarkClick(ad)}
                    >
                      <Card.Img
                        variant="top"
                        src={ad.photo || '/default-pet-image.svg'}
                        className="card-image"
                        onError={(e) => {
                          e.target.src = '/default-pet-image.svg';
                        }}
                      />
                      <Card.Body>
                        <div className={`status-badge status-${ad.status}`}>
                          {getStatusLabel(ad.status)}
                        </div>
                        <Card.Title>{ad.title}</Card.Title>
                        <div className="pet-info">
                          <span className="pet-type">
                            <FaPaw /> {getTypeLabel(ad.type)}
                          </span>
                          {ad.location && (
                            <span className="location">
                              <FaMapMarkerAlt /> {ad.location}
                            </span>
                          )}
                        </div>
                        <Button 
                          variant="outline-primary" 
                          size="sm" 
                          className="w-100"
                          onClick={(e) => {
                            e.stopPropagation();
                            handleShowDetails(ad);
                          }}
                        >
                          Подробнее
                        </Button>
                      </Card.Body>
                    </Card>
                  ))}
                </div>
              )}
            </div>
          </Col>

          <Col md={9} className="map-container">
            <YMaps query={{ apikey: YANDEX_MAPS_API_KEY }}>
              <Map
                defaultState={mapState}
                width="100%"
                height="100%"
                modules={['control.ZoomControl', 'control.FullscreenControl', 'control.SearchControl']}
                onLoad={handleMapLoad}
                onClick={handleMapClick}
                instanceRef={map => setMapRef(map)}
              >
                <SearchControl options={{ float: 'right' }} />
                <ZoomControl options={{ float: 'right' }} />
                
                {advertisements.map(ad => (
                  ad.latitude && ad.longitude ? (
                    <Placemark
                      key={ad.id}
                      geometry={[ad.latitude, ad.longitude]}
                      options={{
                        preset: ad.status === 'lost' ? 'islands#redDotIcon' : 'islands#greenDotIcon',
                        iconColor: ad.status === 'lost' ? '#FF0000' : '#00FF00'
                      }}
                      properties={{
                        balloonContentHeader: ad.title,
                        balloonContentBody: `
                          <div style="padding: 10px;">
                            ${ad.photo ? `<img src="${ad.photo}" 
                                 style="width: 150px; height: 100px; object-fit: cover; border-radius: 8px;" />` : '<div style="width: 150px; height: 100px; background: #f0f0f0; border-radius: 8px; display: flex; align-items: center; justify-content: center; color: #666;">Фото отсутствует</div>'}
                            <p>${ad.description}</p>
                            <p><strong>Статус:</strong> ${getStatusLabel(ad.status)}</p>
                            <p><strong>Тип:</strong> ${getTypeLabel(ad.type)}</p>
                            ${ad.breed ? `<p><strong>Порода:</strong> ${ad.breed}</p>` : ''}
                            <p><strong>Цвет:</strong> ${getColorLabel(ad.color)}</p>
                            <p><strong>Пол:</strong> ${getSexLabel(ad.sex)}</p>
                            <p><strong>Местоположение:</strong> ${ad.location || 'Определяется...'}</p>
                            <p><strong>Автор:</strong> ${ad.author}</p>
                            <p><strong>Телефон:</strong> ${ad.phone || 'Не указан'}</p>
                            ${ad.social_media ? `<p><strong>Соцсети:</strong> <a href="${ad.social_media}" target="_blank">Ссылка</a></p>` : ''}
                          </div>
                        `,
                        balloonContentFooter: `
                          ${ad.photo ? `<button style="padding: 5px 10px; margin: 5px; background: #007bff; color: white; border: none; border-radius: 4px;" 
                                  onclick="window.open('${ad.photo}', '_blank')">
                            Открыть фото
                          </button>` : ''}
                        `
                      }}
                      onClick={() => handleShowDetails(ad)}
                    />
                  ) : null
                ))}

                {newMarkerPosition && (
                  <Placemark
                    geometry={newMarkerPosition}
                    options={{
                      preset: 'islands#blueCircleDotIcon',
                      draggable: true
                    }}
                    onDragEnd={handleMarkerDrag}
                  />
                )}
              </Map>
            </YMaps>
          </Col>
        </Row>
      </Container>

      {/* Модальное окно для создания нового объявления */}
      <Modal 
        show={showNewMarkerModal} 
        onHide={() => setShowNewMarkerModal(false)}
        size="md"
      >
        <Modal.Header closeButton>
          <Modal.Title>
            Создать новое объявление
          </Modal.Title>
        </Modal.Header>
        <Modal.Body>
          <Form>
            <Row>
              <Col md={12}>
                <Form.Group className="mb-2">
                  <Form.Label>
                    Описание*
                  </Form.Label>
                  <Form.Control
                    as="textarea"
                    rows={3}
                    value={newMarkerData.description}
                    onChange={(e) => setNewMarkerData({...newMarkerData, description: e.target.value})}
                    required
                    placeholder="Краткое описание питомца..."
                  />
                </Form.Group>
              </Col>
            </Row>

            <Row>
              <Col md={6}>
                <Form.Group className="mb-3">
                  <Form.Label>
                    Тип животного*
                  </Form.Label>
                  <Form.Select
                    value={newMarkerData.type}
                    onChange={(e) => setNewMarkerData({...newMarkerData, type: e.target.value})}
                    required
                  >
                    {animalTypes.map(type => (
                      <option key={type.value} value={type.value}>
                        {type.label}
                      </option>
                    ))}
                  </Form.Select>
                </Form.Group>
              </Col>
              <Col md={6}>
                <Form.Group className="mb-3">
                  <Form.Label>
                    Статус*
                  </Form.Label>
                  <Form.Select
                    value={newMarkerData.status}
                    onChange={(e) => setNewMarkerData({...newMarkerData, status: e.target.value})}
                    required
                  >
                    <option value="lost">Потерян</option>
                    <option value="found">Найден</option>
                  </Form.Select>
                </Form.Group>
              </Col>
            </Row>

            <Row>
              <Col md={6}>
                <Form.Group className="mb-3">
                  <Form.Label>
                    Порода
                  </Form.Label>
                  <Form.Select
                    value={newMarkerData.breed}
                    onChange={(e) => setNewMarkerData({...newMarkerData, breed: e.target.value})}
                  >
                    <option value="">Выберите породу</option>
                    {breeds.map(breed => (
                      <option key={breed} value={breed}>
                        {breed}
                      </option>
                    ))}
                  </Form.Select>
                </Form.Group>
              </Col>
              <Col md={6}>
                <Form.Group className="mb-3">
                  <Form.Label>
                    Цвет
                  </Form.Label>
                  <Form.Select
                    value={newMarkerData.color}
                    onChange={(e) => setNewMarkerData({...newMarkerData, color: e.target.value})}
                  >
                    {colorOptions.map(option => (
                      <option key={option.value} value={option.value}>
                        {option.label}
                      </option>
                    ))}
                  </Form.Select>
                </Form.Group>
              </Col>
            </Row>

            <Row>
              <Col md={6}>
                <Form.Group className="mb-3">
                  <Form.Label>
                    Пол
                  </Form.Label>
                  <Form.Select
                    value={newMarkerData.sex}
                    onChange={(e) => setNewMarkerData({...newMarkerData, sex: e.target.value})}
                  >
                    {sexOptions.map(option => (
                      <option key={option.value} value={option.value}>
                        {option.label}
                      </option>
                    ))}
                  </Form.Select>
                </Form.Group>
              </Col>
              <Col md={6}>
                <Form.Group className="mb-3">
                  <Form.Label>
                    Цвет глаз
                  </Form.Label>
                  <Form.Select
                    value={newMarkerData.eye_color}
                    onChange={(e) => setNewMarkerData({...newMarkerData, eye_color: e.target.value})}
                  >
                    {eyeColorOptions.map(option => (
                      <option key={option.value} value={option.value}>
                        {option.label}
                      </option>
                    ))}
                  </Form.Select>
                </Form.Group>
              </Col>
            </Row>

            <Row>
              <Col md={6}>
                <Form.Group className="mb-3">
                  <Form.Label>
                    Форма мордочки
                  </Form.Label>
                  <Form.Select
                    value={newMarkerData.face_shape}
                    onChange={(e) => setNewMarkerData({...newMarkerData, face_shape: e.target.value})}
                  >
                    {faceShapeOptions.map(option => (
                      <option key={option.value} value={option.value}>
                        {option.label}
                      </option>
                    ))}
                  </Form.Select>
                </Form.Group>
              </Col>
              <Col md={6}>
                <Form.Group className="mb-3">
                  <Form.Label>
                    Особые приметы
                  </Form.Label>
                  <Form.Select
                    value={newMarkerData.special_features}
                    onChange={(e) => setNewMarkerData({...newMarkerData, special_features: e.target.value})}
                  >
                    {specialFeaturesOptions.map(option => (
                      <option key={option.value} value={option.value}>
                        {option.label}
                      </option>
                    ))}
                  </Form.Select>
                </Form.Group>
              </Col>
            </Row>

            <Row>
              <Col md={6}>
                <Form.Group className="mb-3">
                  <Form.Label>
                    Контактный телефон
                  </Form.Label>
                  <Form.Control
                    type="tel"
                    value={newMarkerData.phone}
                    onChange={(e) => setNewMarkerData({...newMarkerData, phone: e.target.value})}
                    placeholder="+7 (XXX) XXX-XX-XX"
                  />
                </Form.Group>
              </Col>
              <Col md={6}>
                <Form.Group className="mb-3">
                  <Form.Label>
                    Ссылка на соцсети
                  </Form.Label>
                  <Form.Control
                    type="url"
                    value={newMarkerData.social_media}
                    onChange={(e) => setNewMarkerData({...newMarkerData, social_media: e.target.value})}
                    placeholder="https://vk.com/..."
                  />
                </Form.Group>
              </Col>
            </Row>

            <Form.Group className="mb-3">
              <Form.Label>
                Фотография
              </Form.Label>
              <div>
                {photoPreview && (
                      <div>
                    <img
                      src={photoPreview}
                      alt="Preview"
                      style={{
                        maxWidth: '100%',
                        maxHeight: '150px',
                        objectFit: 'cover',
                        borderRadius: '4px'
                      }}
                    />
                  </div>
                )}
                <input
                  type="file"
                  ref={fileInputRef}
                  accept="image/*"
                  onChange={handlePhotoChange}
                  style={{ display: 'none' }}
                />
                <Button
                  variant="outline-primary"
                  onClick={() => fileInputRef.current.click()}
                >
                  {photoPreview ? 'Изменить фото' : 'Загрузить фото'}
                </Button>
                  </div>
            </Form.Group>
          </Form>
        </Modal.Body>
        <Modal.Footer>
          <Button variant="secondary" onClick={() => setShowNewMarkerModal(false)}>
            Отмена
          </Button>
          <Button 
            variant="primary"
            onClick={handleCreateNewMarker}
            disabled={isSubmitting || !newMarkerData.description}
          >
            {isSubmitting ? 'Создание...' : 'Создать'}
          </Button>
        </Modal.Footer>
      </Modal>

      {/* Модальное окно с подробной информацией */}
      <Modal show={showModal} onHide={() => setShowModal(false)} size="lg">
        <Modal.Header closeButton>
          <Modal.Title>{selectedAd?.title}</Modal.Title>
        </Modal.Header>
        <Modal.Body>
          {selectedAd && (
            <div className="advertisement-details">
              <div className="advertisement-image">
                {selectedAd.photo && (
                  <img src={selectedAd.photo} alt={selectedAd.title} className="img-fluid" />
                )}
                  </div>
              <div className="advertisement-info">
                <h4>Информация о животном</h4>
                <p><strong>Статус:</strong> {getStatusLabel(selectedAd.status)}</p>
                <p><strong>Тип:</strong> {getTypeLabel(selectedAd.type)}</p>
                <p><strong>Порода:</strong> {selectedAd.breed || 'Не указана'}</p>
                <p><strong>Цвет:</strong> {getColorLabel(selectedAd.color)}</p>
                <p><strong>Пол:</strong> {getSexLabel(selectedAd.sex)}</p>
                <p><strong>Цвет глаз:</strong> {getEyeColorLabel(selectedAd.eye_color)}</p>
                <p><strong>Форма мордочки:</strong> {getFaceShapeLabel(selectedAd.face_shape)}</p>
                <p><strong>Особые приметы:</strong> {getSpecialFeaturesLabel(selectedAd.special_features)}</p>
                <p><strong>Описание:</strong> {selectedAd.description}</p>
                <p><strong>Местоположение:</strong> {selectedAd.location || 'Определяется...'}</p>
                <p><strong>Автор:</strong> {selectedAd.author}</p>
                <p><strong>Контактный телефон:</strong> {selectedAd.phone || 'Не указан'}</p>
                {selectedAd.social_media && (
                  <p><strong>Социальные сети:</strong> <a href={selectedAd.social_media} target="_blank" rel="noopener noreferrer">Ссылка</a></p>
                )}
              </div>
            </div>
          )}
        </Modal.Body>
        <Modal.Footer>
          <Button variant="secondary" onClick={() => setShowModal(false)}>
            Закрыть
          </Button>
        </Modal.Footer>
      </Modal>
      </div>
  );
};

export default SearchByLocation;