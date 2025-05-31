import React, { useState, useEffect, useRef, useCallback } from 'react';
import { Container, Form, Button } from 'react-bootstrap';
import { withRouter, useParams } from 'react-router-dom';
import { FaCamera, FaSave, FaTimes, FaTrash, FaPaw, FaMapMarkerAlt, FaCheck, FaPhone } from 'react-icons/fa';
import NavbarComp from './NavbarComp';
import api from '../../api/config';
import '../../styles/common.css';
import '../../styles/NewPetProfile.css';

// Заглушка для изображения питомца в формате base64
const DEFAULT_PET_IMAGE = 'data:image/svg+xml;base64,PHN2ZyB3aWR0aD0iNDAwIiBoZWlnaHQ9IjMwMCIgeG1sbnM9Imh0dHA6Ly93d3cudzMub3JnLzIwMDAvc3ZnIj48cmVjdCB3aWR0aD0iNDAwIiBoZWlnaHQ9IjMwMCIgZmlsbD0iI2YwZjBmMCIvPjx0ZXh0IHg9IjUwJSIgeT0iNTAlIiBmb250LWZhbWlseT0iQXJpYWwiIGZvbnQtc2l6ZT0iMjAiIHRleHQtYW5jaG9yPSJtaWRkbGUiIGZpbGw9IiM2NjY2NjYiPtCk0L7RgtC+0LPRgNCw0YTQuNGPINC/0LjRgtC+0LzRhtCwPC90ZXh0Pjwvc3ZnPg==';

const PetProfile = ({ match, history }) => {
  const [pet, setPet] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');
  const [isEditMode, setIsEditMode] = useState(true);
  const fileInputRef = useRef(null);
  const [breeds, setBreeds] = useState([]);
  const { id } = useParams();

  const animalTypes = [
    { value: 'cat', label: 'Кошка' },
    { value: 'dog', label: 'Собака' },
    { value: 'bird', label: 'Птица' },
    { value: 'rodent', label: 'Грызун' },
    { value: 'rabbit', label: 'Кролик' },
    { value: 'reptile', label: 'Рептилия' },
    { value: 'other', label: 'Другое животное' }
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

  // Базовое состояние формы
  const [formData, setFormData] = useState({
    status: 'lost',
    date: new Date().toISOString().split('T')[0],
    title: '',
    description: '',
    type: '',
    breed: '',
    sex: 'unknown',
    color: 'white',
    eye_color: 'yellow',
    face_shape: 'round',
    special_features: 'none',
    features: '',
    photos: [],
    contact_name: '',
    phone: '',
    email: '',
    location: '',
    latitude: 0,
    longitude: 0,
    social_media: '',
    author: ''
  });

  // Загрузка данных пользователя и инициализация формы
  useEffect(() => {
    const loadUserDataAndInitForm = async () => {
      try {
        setLoading(true);
        const token = localStorage.getItem('jwtToken');
        if (!token) {
          history.push('/login');
          return;
        }

        // Получаем данные текущего пользователя
        const userResponse = await api.get('/api/users/current/');
        const userData = userResponse.data;

        if (!userData || !userData.username) {
          throw new Error('Некорректный ответ от сервера');
        }

        // Если это новое объявление
        if (!id || id === 'new') {
          setFormData(prev => ({
            ...prev,
            contact_name: userData.username || '',
            phone: userData.profile?.phone || '',
            email: userData.email || '',
            author: userData.username
          }));
        } else {
          // Если это существующее объявление
          const petResponse = await api.get(`/api/advertisements/${id}/`);
          setPet(petResponse.data);
          setFormData(petResponse.data);
          setIsEditMode(false);
        }
      } catch (error) {
        console.error('Ошибка при загрузке данных:', error);
        if (error.response?.status === 401) {
          localStorage.removeItem('jwtToken');
          history.push('/login');
          return;
        }
        setError('Ошибка при загрузке данных. Пожалуйста, попробуйте позже.');
      } finally {
        setLoading(false);
      }
    };

    loadUserDataAndInitForm();
  }, [id, history]);

  const getCoordinatesFromAddress = async (address) => {
    try {
      const response = await fetch(`https://nominatim.openstreetmap.org/search?format=json&q=${encodeURIComponent(address)}`);
      const data = await response.json();
      if (data && data.length > 0) {
        return {
          latitude: parseFloat(data[0].lat),
          longitude: parseFloat(data[0].lon)
        };
      }
      // Если координаты не найдены, возвращаем дефолтные значения для Москвы
      return {
        latitude: 55.7558,
        longitude: 37.6173
      };
    } catch (error) {
      console.error('Ошибка при получении координат:', error);
      // В случае ошибки также возвращаем дефолтные значения
      return {
        latitude: 55.7558,
        longitude: 37.6173
      };
    }
  };

  const handleLocationChange = async (e) => {
    const location = e.target.value;
    setFormData(prev => ({ ...prev, location }));
    
    if (location) {
      const coordinates = await getCoordinatesFromAddress(location);
      setFormData(prev => ({
        ...prev,
        latitude: coordinates.latitude,
        longitude: coordinates.longitude
      }));
    }
  };

  const fetchBreeds = useCallback(async () => {
    if (!formData.type) {
      setBreeds([]);
      return;
    }

    try {
      const response = await api.get('/api/users/breeds/', {
        params: { type: formData.type }
      });
      setBreeds(response.data || []);
    } catch (error) {
      console.error('Ошибка при загрузке пород:', error);
      setBreeds(['Другая']);
    }
  }, [formData.type]);

  useEffect(() => {
    fetchBreeds();
  }, [fetchBreeds]);

  const handleInputChange = (e) => {
    const { name, value } = e.target;
    console.log(`Изменение поля ${name}:`, value);
    setFormData(prev => {
      const updated = {
        ...prev,
        [name]: value
      };
      console.log('Обновленное состояние формы:', updated);
      return updated;
    });
    setError('');
  };

  const handlePhotoChange = async (e) => {
    const files = Array.from(e.target.files);
    if (files.length > 0) {
      try {
        setLoading(true);
        
        // Проверяем размер файлов
        files.forEach(file => {
          if (file.size > 5 * 1024 * 1024) {
            throw new Error('Размер файла не должен превышать 5MB');
          }
        });

        // Сохраняем файлы для последующей отправки
        setFormData(prev => ({
          ...prev,
          photoFiles: files,
          photos: files.map(file => URL.createObjectURL(file))
        }));

        setSuccess('Фотографии успешно добавлены');
      } catch (error) {
        setError(error.message || 'Ошибка при добавлении фотографий');
      } finally {
        setLoading(false);
      }
    }
  };

  const handleRemovePhoto = (index) => {
    setFormData(prev => {
      const newPhotos = [...prev.photos];
      const newPhotoFiles = [...(prev.photoFiles || [])];
      
      // Удаляем URL объекта
      if (newPhotos[index]) {
        URL.revokeObjectURL(newPhotos[index]);
      }
      
      newPhotos.splice(index, 1);
      newPhotoFiles.splice(index, 1);
      
      return {
        ...prev,
        photos: newPhotos,
        photoFiles: newPhotoFiles
      };
    });
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError('');
    setSuccess('');

    // Проверяем все обязательные поля
    const trimmedData = {
      ...formData,
      title: formData.title?.trim() || '',
      description: formData.description?.trim() || '',
      contact_name: formData.contact_name?.trim() || '',
      phone: formData.phone?.trim() || '',
      email: formData.email?.trim() || '',
      location: formData.location?.trim() || ''
    };

    // Проверка обязательных полей
    const requiredFields = {
      title: 'Заголовок',
      description: 'Описание',
      type: 'Тип животного',
      contact_name: 'Контактное имя',
      phone: 'Телефон',
      location: 'Местоположение'
    };

    const missingFields = Object.entries(requiredFields)
      .filter(([key]) => !trimmedData[key])
      .map(([, label]) => label);

    // Проверяем наличие фотографии
    if (!formData.photoFiles || formData.photoFiles.length === 0) {
      missingFields.push('Фотография питомца');
    }

    if (missingFields.length > 0) {
      setError(`Пожалуйста, заполните следующие обязательные поля: ${missingFields.join(', ')}`);
      setLoading(false);
      return;
    }

    try {
      const coordinates = await getCoordinatesFromAddress(trimmedData.location);
      
      // Создаем FormData для отправки файлов
      const formDataToSend = new FormData();
      
      // Добавляем все поля формы
      Object.keys(trimmedData).forEach(key => {
        if (key !== 'photos' && key !== 'photoFiles') {
          formDataToSend.append(key, trimmedData[key]);
        }
      });

      // Добавляем координаты
      formDataToSend.append('latitude', coordinates.latitude);
      formDataToSend.append('longitude', coordinates.longitude);

      // Если есть новые фотографии, добавляем первую как основную
      if (formData.photoFiles && formData.photoFiles.length > 0) {
        formDataToSend.append('photo', formData.photoFiles[0]);
      }

      let response;
      if (id && id !== 'new') {
        response = await api.put(`/api/advertisements/${id}/`, formDataToSend, {
          headers: {
            'Content-Type': 'multipart/form-data'
          }
        });
        setSuccess('Объявление успешно обновлено');
      } else {
        response = await api.post('/api/advertisements/', formDataToSend, {
          headers: {
            'Content-Type': 'multipart/form-data'
          }
        });
        setSuccess('Объявление успешно создано');
      }

      history.push(`/advertisement/${response.data.id}`);
    } catch (error) {
      console.error('Ошибка при сохранении объявления:', error);
      setError(
        error.response?.data?.detail || 
        error.response?.data?.message || 
        'Произошла ошибка при сохранении объявления'
      );
    } finally {
      setLoading(false);
    }
  };

  const handleDelete = async () => {
    if (window.confirm('Вы уверены, что хотите удалить это объявление?')) {
      try {
        setLoading(true);
        await api.delete(`/api/advertisements/${match.params.id}/`);
        history.push('/home');
      } catch (error) {
        setError('Ошибка при удалении объявления');
        setLoading(false);
      }
    }
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

  return (
    <>
      <NavbarComp />
      <div className="pet-profile-container">
        <Container>
          <div className="pet-profile-card">
            <h1 className="pet-profile-title">
              {match.params.id === 'new' ? 'Создание объявления о питомце' : (pet?.name ? `Питомец ${pet.name}` : 'Профиль питомца')}
            </h1>

            {error && (
              <div className="alert alert-danger">
                <FaTimes /> {error}
              </div>
            )}
            {success && (
              <div className="alert alert-success">
                <FaCheck /> {success}
              </div>
            )}

            <Form onSubmit={handleSubmit}>
              <div className="pet-photo-section">
                <div className="pet-photo-container" onClick={() => fileInputRef.current?.click()}>
                  <img
                    src={(formData.photos && formData.photos.length > 0) ? formData.photos[0] : DEFAULT_PET_IMAGE}
                    alt="Фотография питомца"
                    className="pet-photo"
                  />
                  <div className="photo-overlay">
                    <FaCamera className="camera-icon" />
                    <span className="photo-hint">Нажмите, чтобы добавить фотографию питомца</span>
                  </div>
                </div>
                <input
                  type="file"
                  ref={fileInputRef}
                  onChange={handlePhotoChange}
                  accept="image/*"
                  multiple
                  style={{ display: 'none' }}
                />
              </div>

              {formData.photos.length > 0 && (
                <div className="photo-gallery">
                  {formData.photos.map((photo, index) => (
                    <div key={index} className="gallery-item">
                      <img src={photo} alt={`Фото ${index + 1}`} />
                      {isEditMode && (
                        <button
                          type="button"
                          className="remove-photo"
                          onClick={() => handleRemovePhoto(index)}
                        >
                          <FaTimes />
                        </button>
                      )}
                    </div>
                  ))}
                </div>
              )}

              <div className="form-section">
                <h3 className="section-title">
                  <FaPaw />
                  Основная информация о питомце
                </h3>
                
                <Form.Group className="form-group">
                  <Form.Label>Заголовок объявления*</Form.Label>
                  <Form.Control
                    type="text"
                    name="title"
                    value={formData.title}
                    onChange={handleInputChange}
                    disabled={!isEditMode}
                    placeholder="Например: Пропал рыжий кот в районе ул. Ленина"
                    required
                  />
                </Form.Group>

                <Form.Group className="form-group">
                  <Form.Label>Статус объявления</Form.Label>
                  <Form.Control
                    as="select"
                    name="status"
                    value={formData.status}
                    onChange={handleInputChange}
                    disabled={!isEditMode}
                  >
                    <option value="lost">Пропал питомец</option>
                    <option value="found">Найден питомец</option>
                  </Form.Control>
                </Form.Group>
            
                <Form.Group className="form-group">
                <Form.Label>Тип животного</Form.Label>
                <Form.Control
                  as="select"
                  name="type"
                    value={formData.type}
                  onChange={handleInputChange}
                  disabled={!isEditMode}
                >
                    <option value="">Укажите, кто ваш питомец</option>
                    {animalTypes.map(type => (
                      <option key={type.value} value={type.value}>
                        {type.label}
                      </option>
                    ))}
                </Form.Control>
              </Form.Group>

                <Form.Group className="form-group">
                  <Form.Label>Порода питомца</Form.Label>
                  <Form.Control
                    as="select"
                    name="breed"
                    value={formData.breed}
                    onChange={handleInputChange}
                    disabled={!isEditMode || !formData.type}
                  >
                    <option value="">
                      {!formData.type 
                        ? 'Сначала выберите тип питомца' 
                        : 'Выберите породу питомца'}
                    </option>
                    {breeds.map(breed => (
                      <option key={breed} value={breed}>
                        {breed}
                      </option>
                    ))}
                  </Form.Control>
                  {isEditMode && formData.breed === 'Другая' && (
                    <Form.Control
                      type="text"
                      name="customBreed"
                      value={formData.customBreed || ''}
                      onChange={handleInputChange}
                      placeholder="Укажите породу питомца"
                      className="mt-2"
                    />
                  )}
                </Form.Group>

                <Form.Group className="form-group">
                  <Form.Label>Пол питомца</Form.Label>
                <Form.Control
                  as="select"
                  name="sex"
                    value={formData.sex}
                  onChange={handleInputChange}
                  disabled={!isEditMode}
                >
                    {sexOptions.map(option => (
                      <option key={option.value} value={option.value}>
                        {option.label}
                      </option>
                    ))}
                </Form.Control>
              </Form.Group>

                <Form.Group className="form-group">
                  <Form.Label>Цвет</Form.Label>
  <Form.Control
    as="select"
                    name="color"
                    value={formData.color}
    onChange={handleInputChange}
    disabled={!isEditMode}
  >
                    {colorOptions.map(option => (
                      <option key={option.value} value={option.value}>
                        {option.label}
                      </option>
                    ))}
                  </Form.Control>
                </Form.Group>

                <Form.Group className="form-group">
                  <Form.Label>Цвет глаз</Form.Label>
                  <Form.Control
                    as="select"
                    name="eye_color"
                    value={formData.eye_color}
                    onChange={handleInputChange}
                    disabled={!isEditMode}
                  >
                    {eyeColorOptions.map(option => (
                      <option key={option.value} value={option.value}>
                        {option.label}
                      </option>
                    ))}
  </Form.Control>
</Form.Group>

                <Form.Group className="form-group">
                  <Form.Label>Форма мордочки</Form.Label>
                <Form.Control
                  as="select"
                    name="face_shape"
                    value={formData.face_shape}
                  onChange={handleInputChange}
                  disabled={!isEditMode}
                >
                    {faceShapeOptions.map(option => (
                      <option key={option.value} value={option.value}>
                        {option.label}
                      </option>
                    ))}
                </Form.Control>
              </Form.Group>

                <Form.Group className="form-group">
                  <Form.Label>Особые приметы</Form.Label>
                  <Form.Control
                    as="select"
                    name="special_features"
                    value={formData.special_features}
                    onChange={handleInputChange}
                    disabled={!isEditMode}
                  >
                    {specialFeaturesOptions.map(option => (
                      <option key={option.value} value={option.value}>
                        {option.label}
                      </option>
                    ))}
                  </Form.Control>
                </Form.Group>
              </div>

              <div className="form-section">
                <h3 className="section-title">
                  <FaMapMarkerAlt />
                  {formData.status === 'lost' 
                    ? 'Где и когда пропал питомец' 
                    : 'Где и когда найден питомец'}
                </h3>
                
                <Form.Group className="form-group">
                  <Form.Label>Адрес*</Form.Label>
                  <Form.Control
                    type="text"
                    name="location"
                    value={formData.location}
                    onChange={handleLocationChange}
                    disabled={!isEditMode}
                    placeholder="Укажите адрес или район, например: ул. Ленина, д. 1 или район Центральный"
                    required
                  />
                </Form.Group>

                <Form.Group className="form-group">
                  <Form.Label>Описание места и обстоятельств</Form.Label>
                  <Form.Control
                    as="textarea"
                    rows={4}
                    name="description"
                    value={formData.description}
                    onChange={handleInputChange}
                    disabled={!isEditMode}
                    placeholder={formData.status === 'lost' 
                      ? "Опишите подробно, где и при каких обстоятельствах пропал питомец. Например: убежал со двора, последний раз видели возле магазина, был в красном ошейнике и т.д."
                      : "Опишите подробно, где и при каких обстоятельствах найден питомец. Например: найден в подъезде дома №5, ходит по району несколько дней, ласковый, в синем ошейнике и т.д."}
                  />
                </Form.Group>
              </div>

              <div className="form-section">
                <h3 className="section-title">
                  <FaPhone />
                  Контактная информация
                </h3>
                
                <Form.Group className="form-group">
                  <Form.Label>Контактное лицо*</Form.Label>
                  <Form.Control
                    type="text"
                    name="contact_name"
                    value={formData.contact_name}
                    onChange={handleInputChange}
                    disabled={!isEditMode}
                    placeholder="Как к вам обращаться"
                    required
                  />
                </Form.Group>

                <Form.Group className="form-group">
                  <Form.Label>Телефон*</Form.Label>
                  <Form.Control
                    type="tel"
                    name="phone"
                    value={formData.phone}
                    onChange={handleInputChange}
                    disabled={!isEditMode}
                    placeholder="+7 (XXX) XXX-XX-XX"
                    required
                  />
                </Form.Group>

                <Form.Group className="form-group">
                  <Form.Label>Email</Form.Label>
                  <Form.Control
                    type="email"
                    name="email"
                    value={formData.email}
                    onChange={handleInputChange}
                    disabled={!isEditMode}
                    placeholder="example@mail.com"
                  />
                </Form.Group>

                <Form.Group className="form-group">
                  <Form.Label>Ссылка на социальные сети</Form.Label>
                  <Form.Control
                    type="url"
                    name="social_media"
                    value={formData.social_media}
                    onChange={handleInputChange}
                    disabled={!isEditMode}
                    placeholder="https://vk.com/username"
                  />
                </Form.Group>
              </div>

              <div className="button-group">
                {isEditMode ? (
                <>
                    <Button
                      type="submit"
                      className="action-button save-button"
                      disabled={loading}
                    >
                      <FaSave />
                      {loading ? 'Сохранение...' : 'Сохранить информацию'}
                    </Button>
                    {match.params.id !== 'new' && (
                      <Button
                        type="button"
                        className="action-button cancel-button"
                        onClick={() => setIsEditMode(false)}
                        disabled={loading}
                      >
                        <FaTimes />
                        Отменить изменения
                      </Button>
                    )}
                  </>
                ) : (
                  <>
                    <Button
                      type="button"
                      className="action-button save-button"
                      onClick={() => setIsEditMode(true)}
                      disabled={loading}
                    >
                      <FaPaw />
                      Редактировать информацию
                  </Button>
                    <Button
                      type="button"
                      className="action-button delete-button"
                      onClick={handleDelete}
                      disabled={loading}
                    >
                      <FaTrash />
                      Удалить объявление
                  </Button>
                </>
              )}
              </div>
            </Form>
          </div>
      </Container>
      </div>
    </>
  );
};

export default withRouter(PetProfile);
