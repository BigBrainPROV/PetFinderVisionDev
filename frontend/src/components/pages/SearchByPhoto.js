import React, { useState } from 'react';
import { Container } from 'react-bootstrap';
import { FaCloudUploadAlt, FaPaw, FaEye } from 'react-icons/fa';
import NavbarComp from './NavbarComp';
import api from '../../api/config';
import '../../styles/common.css';
import '../../styles/SearchByPhoto.css';

const SearchByPhoto = () => {
  const [selectedFile, setSelectedFile] = useState(null);
  const [preview, setPreview] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [similarPets, setSimilarPets] = useState([]);
  const [analysis, setAnalysis] = useState(null);

  const translations = {
    // Базовые цвета
    'black': 'черный',
    'white': 'белый',
    'gray': 'серый',
    'brown': 'коричневый',
    'red': 'рыжий',
    'spotted': 'пятнистый',
    'multicolor': 'многоцветный',
    'bengal': 'бенгальский',
    'золотистый': 'золотистый',
    'серый': 'серый',
    'коричневый': 'коричневый',
    'белый': 'белый',
    'черный': 'черный',
    'рыжий': 'рыжий',
    'смешанный': 'смешанный',

    // Цвета глаз
    'blue': 'голубой',
    'green': 'зеленый',
    'yellow': 'желтый',
    'orange': 'оранжевый',
    'copper': 'медный',
    'different': 'разные',

    // Форма мордочки
    'round': 'круглая',
    'oval': 'овальная',
    'triangular': 'треугольная',
    'long': 'вытянутая',

    // Особые приметы
    'spotted_pattern': 'пятнистый узор',
    'heterochromia': 'разные глаза',
    'гетерохромия': 'разные глаза',
    'ear_fold': 'вислоухость',
    'залом на ухе': 'залом на ухе',
    'нет глаза': 'нет глаза',
    'eye_spot': 'пятно у глаза',
    'none': 'отсутствуют',

    // Типы животных
    'cat': 'кошка',
    'dog': 'собака',
    'bird': 'птица',
    'rodent': 'грызун',
    'rabbit': 'кролик',
    'reptile': 'рептилия',
    'other': 'другое',

    // Породы
    'беспородная': 'беспородная',
    'домашняя': 'домашняя',
    'голубь': 'голубь',
    'попугай': 'попугай',
    'канарейка': 'канарейка',
    'волнистый попугайчик': 'волнистый попугайчик',
    'хомяк': 'хомяк',
    'крыса': 'крыса',
    'мышь': 'мышь',
    'морская свинка': 'морская свинка',
    'домашний': 'домашний кролик',
    'карликовый': 'карликовый кролик',

    // Другие термины
    'pseudo': 'псевдо-анализ',
    'unknown': 'неизвестно',
    'неизвестно': 'неизвестно'
  };

  const formatLabel = (label) => {
    if (!label) return 'неизвестно';
    if (typeof label === 'string' && label.startsWith('RGB')) return label;
    return translations[label] || label;
  };

  const formatConfidence = (confidence) => {
    return `${Math.round((confidence || 0) * 100)}%`;
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
      setSimilarPets([]);
      setAnalysis(null);
    }
  };

  const handleSearch = async () => {
    if (!selectedFile) {
      setError('Пожалуйста, выберите изображение');
      return;
    }

    setLoading(true);
    setError('');
    setSimilarPets([]);
    setAnalysis(null);

    try {
      // Отправляем файл как multipart/form-data в ML сервис
      const formData = new FormData();
      formData.append('file', selectedFile);

      console.log('Отправляем файл в ML сервис:', {
        name: selectedFile.name,
        size: selectedFile.size,
        type: selectedFile.type
      });
      
      const searchResponse = await fetch('http://localhost:5004/search/', {
        method: 'POST',
        body: formData  // FormData автоматически устанавливает правильный Content-Type
      });

      if (!searchResponse.ok) {
        const errorText = await searchResponse.text();
        throw new Error(`Ошибка ML сервиса: ${errorText}`);
      }

      const searchData = await searchResponse.json();
      console.log('Результаты анализа фото:', searchData);

      if (searchData.error) {
        throw new Error(searchData.error);
      }

      // Обрабатываем новый формат ответа от ML сервиса
      if (searchData.analysis) {
        const analysis = {
          animalType: searchData.analysis.animal_type,
          breed: searchData.analysis.breed,
          color: searchData.analysis.color,
          features: searchData.analysis.features,
          confidence: searchData.analysis.confidence,
          bodyProportions: searchData.analysis.body_proportions,
          uniqueFeatures: searchData.analysis.unique_features
        };
        setAnalysis(analysis);
      }

      // Обрабатываем найденные объявления о потерянных питомцах
      if (searchData.similar_lost_pets && searchData.similar_lost_pets.length > 0) {
        console.log('Найдены объявления о потерянных питомцах:', searchData.similar_lost_pets);
        
        // Преобразуем в нужный формат для отображения
        const lostPets = searchData.similar_lost_pets.map(pet => {
          // Формируем правильный URL для изображения
          let photoUrl = null;
          if (pet.image_url) {
            if (pet.image_url.startsWith('http')) {
              // Уже полный URL
              photoUrl = pet.image_url;
            } else {
              // Относительный путь, добавляем базовый URL
              photoUrl = `http://localhost:8000/uploads/${pet.image_url}`;
            }
          }
          
          return {
            id: pet.id,
            title: pet.title,
            description: pet.description,
            breed: pet.breed,
            color: pet.color,
            photo: photoUrl,
            similarity: pet.similarity || 1.0,
            vectorSimilarity: false,
            matchedFeatures: pet.features || ['характеристики породы'],
            animalType: pet.animal_type,
            lostDate: pet.lost_date,
            contact: pet.contact,
            lostLocation: pet.lost_location
          };
        });
        
        setSimilarPets(lostPets);
        console.log(`Найдено ${lostPets.length} объявлений о потерянных питомцах`);
        console.log('Обработанные объявления:', lostPets.map(pet => ({
          id: pet.id,
          title: pet.title,
          photo: pet.photo
        })));
      } else {
        console.log('Не найдено подходящих объявлений');
        setSimilarPets([]);
      }

    } catch (error) {
      console.error('Ошибка при поиске:', error);
      setError(error.message || 'Произошла ошибка при поиске. Пожалуйста, попробуйте позже.');
    } finally {
      setLoading(false);
    }
  };

  const renderAnalysis = () => {
    if (!analysis) return null;

    const features = [];

    // Добавляем тип животного
    if (analysis.animalType) {
      features.push({
        label: 'Тип животного',
        value: formatLabel(analysis.animalType.label),
        confidence: analysis.animalType.confidence,
        description: 'Определенный тип животного'
      });
    }

    // Добавляем породу
    if (analysis.breed) {
      features.push({
        label: 'Порода',
        value: formatLabel(analysis.breed.label),
        confidence: analysis.breed.confidence,
        description: 'Определенная порода животного'
      });
    }

    // Добавляем цвет и паттерн
    if (analysis.color) {
      features.push({
        label: 'Цвет',
        value: `${formatLabel(analysis.color.label)} (${analysis.color.pattern || 'сплошной'})`,
        confidence: analysis.color.confidence,
        description: 'Основной цвет и паттерн окраса'
      });
    }

    // Добавляем особенности из features
    if (analysis.features && analysis.features.length > 0) {
      const featureLabels = analysis.features
        .filter(f => f.label !== 'pseudo')
        .map(f => formatLabel(f.label))
        .join(', ');
      
      if (featureLabels) {
        features.push({
          label: 'Особые характеристики',
          value: featureLabels,
          confidence: 0.9,
          description: 'Обнаруженные особенности и характеристики'
        });
      }
    }

    // Добавляем уникальные особенности
    if (analysis.uniqueFeatures) {
      const uniqueFeaturesList = [];
      
      if (analysis.uniqueFeatures.heterochromia?.present) {
        uniqueFeaturesList.push('гетерохромия (разные глаза)');
      }
      if (analysis.uniqueFeatures.ear_fold?.present) {
        uniqueFeaturesList.push('залом на ухе');
      }
      if (analysis.uniqueFeatures.missing_eye?.present) {
        uniqueFeaturesList.push('нет глаза');
      }
      if (analysis.uniqueFeatures.flat_face?.present) {
        uniqueFeaturesList.push('плоская морда');
      }
      if (analysis.uniqueFeatures.short_tail?.present) {
        uniqueFeaturesList.push('короткий хвост');
      }

      if (uniqueFeaturesList.length > 0) {
        features.push({
          label: 'Уникальные особенности',
          value: uniqueFeaturesList.join(', '),
          confidence: 1.0,
          description: 'Специальные характеристики внешности'
        });
      }
    }

    // Добавляем пропорции тела
    if (analysis.bodyProportions) {
      features.push({
        label: 'Телосложение',
        value: `${analysis.bodyProportions.size_category || 'средний'} размер`,
        confidence: 0.8,
        description: 'Размерная категория животного'
      });
    }

    // Добавляем общую уверенность
    if (analysis.confidence) {
      features.push({
        label: 'Общая точность',
        value: `${formatConfidence(analysis.confidence)} уверенности`,
        confidence: analysis.confidence,
        description: 'Общая точность анализа изображения'
      });
    }

    return (
      <div className="analysis-results">
        <h3>Результаты анализа изображения:</h3>
        <div className="features-grid">
          {features.map((feature, index) => (
            <div key={index} className="feature-card">
              <h4>{feature.label}</h4>
              <p className="feature-value">{feature.value}</p>
              <div className="confidence-bar">
                <div 
                  className="confidence-fill" 
                  style={{ width: `${(feature.confidence || 0) * 100}%` }}
                />
                <span className="confidence-text">
                  {formatConfidence(feature.confidence)}
                </span>
              </div>
              <small className="feature-description">{feature.description}</small>
            </div>
          ))}
        </div>
      </div>
    );
  };

  const renderPetCard = (pet) => (
    <div key={pet.id} className="pet-card" onClick={() => window.location.href = `/advertisement/${pet.id}`}>
      <img
        src={pet.photo || 'https://via.placeholder.com/300x200?text=Нет+фото'}
        alt={pet.title}
        className="pet-image"
      />
      <div className="pet-info">
        <h3 className="pet-name">{pet.title}</h3>
        <div className="pet-details">
          <p>{pet.breed} • {pet.color}</p>
          {pet.similarity && (
            <div className="similarity-info">
              <div className={`similarity-badge ${pet.vectorSimilarity ? 'vector-similarity' : 'feature-similarity'}`}>
                {pet.vectorSimilarity ? (
                  <>
                    <FaEye className="similarity-icon" />
                    {`${Math.round(pet.similarity * 100)}% визуальное сходство`}
                  </>
                ) : (
                  <>
                    <FaPaw className="similarity-icon" />
                    {`${Math.round(pet.similarity * 100)}% совпадение характеристик`}
                  </>
                )}
              </div>
              <small className="matched-features">
                {pet.vectorSimilarity ? 
                  'Найдено с помощью нейросети' : 
                  `Совпадения: ${pet.matchedFeatures.join(', ')}`
                }
              </small>
            </div>
          )}
        </div>
      </div>
    </div>
  );

  return (
    <>
      <NavbarComp />
      <div className="search-photo-container">
        <div className="search-header">
          <Container>
            <h1 className="search-title">Поиск по фотографии</h1>
            <p className="search-description">
              Загрузите фотографию питомца, и мы найдем похожих животных в базе объявлений с помощью нейронной сети.
            </p>
          </Container>
        </div>

        <Container>
          <div className="upload-section">
            <div 
              className="upload-area"
              onClick={() => document.getElementById('file-input').click()}
            >
              {preview ? (
                <img src={preview} alt="Preview" className="image-preview" />
              ) : (
                <div className="upload-placeholder">
                  <FaCloudUploadAlt className="upload-icon" />
                  <p>Нажмите для выбора фотографии или перетащите её сюда</p>
                  <small>Поддерживаются форматы: JPG, PNG. Максимальный размер: 5MB</small>
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
            <button 
              className="search-button" 
              onClick={handleSearch}
              disabled={!selectedFile || loading}
            >
              {loading ? 'Поиск...' : 'Найти похожих питомцев'}
            </button>
          </div>

          {error && (
            <div className="error-message">
              {error}
            </div>
          )}

          {loading && (
            <div className="loading-container">
              <div className="spinner"></div>
              <p>Анализируем изображение и ищем похожих питомцев...</p>
            </div>
          )}

          {renderAnalysis()}

          {similarPets.length > 0 && (
            <div className="search-results">
              <h2>Похожие питомцы:</h2>
              <div className="pets-grid">
                {similarPets.map(renderPetCard)}
              </div>
            </div>
          )}
        </Container>
      </div>
    </>
  );
};

export default SearchByPhoto;
