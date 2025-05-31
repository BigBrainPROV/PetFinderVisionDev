import React, { useState, useEffect } from 'react';
import { Form, Button } from 'react-bootstrap';
import { useHistory } from 'react-router-dom';
import { FaSearch, FaFilter } from 'react-icons/fa';
import NavbarComp from './NavbarComp';
import api from '../../api/config';
import '../../styles/common.css';
import '../../styles/SearchByPost.css';

const SearchByPost = () => {
  const [searchParams, setSearchParams] = useState({
    type: '',
    status: '',
    query: ''
  });
  const [searchResults, setSearchResults] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const history = useHistory();

  const animalTypes = [
    { value: 'all', label: 'Все животные' },
    { value: 'cat', label: 'Кошка' },
    { value: 'dog', label: 'Собака' },
    { value: 'bird', label: 'Птица' },
    { value: 'rodent', label: 'Грызун' },
    { value: 'rabbit', label: 'Кролик' },
    { value: 'reptile', label: 'Рептилия' },
    { value: 'other', label: 'Другое животное' }
  ];

  useEffect(() => {
    fetchAllAdvertisements();
  }, []);

  const fetchAllAdvertisements = async () => {
    try {
      setLoading(true);
      setError('');
      const response = await api.get('/api/advertisements/');
      if (response.data) {
        const filteredAds = response.data.filter(ad => 
          ad.title !== "Temporary" && ad.description !== "Temporary"
        );
        setSearchResults(filteredAds);
      }
    } catch (error) {
      console.error('Ошибка при загрузке объявлений:', error);
      setError('Произошла ошибка при загрузке объявлений');
    } finally {
      setLoading(false);
    }
  };

  const handleInputChange = (e) => {
    const { name, value } = e.target;
    setSearchParams(prev => ({
      ...prev,
      [name]: value
    }));
  };

  const handleSearch = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError('');

    try {
      const queryParams = new URLSearchParams();
      if (searchParams.type && searchParams.type !== 'all') {
        queryParams.append('type', searchParams.type);
      }
      if (searchParams.status) {
        queryParams.append('status', searchParams.status);
      }
      if (searchParams.query) {
        queryParams.append('q', searchParams.query);
      }

      if (queryParams.toString() === '') {
        await fetchAllAdvertisements();
        return;
      }

      const response = await api.get(`/api/advertisements/search/?${queryParams.toString()}`);
      if (response.data) {
        const filteredAds = response.data.filter(ad => 
          ad.title !== "Temporary" && ad.description !== "Temporary"
        );
        setSearchResults(filteredAds);
      }
    } catch (error) {
      console.error('Ошибка при поиске:', error);
      setError('Произошла ошибка при поиске объявлений');
    } finally {
      setLoading(false);
    }
  };

  const handleViewDetails = (adId) => {
    history.push(`/advertisement/${adId}`);
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

  return (
    <>
      <NavbarComp />
      <div className="search-by-post-container">
        <div className="search-banner">
          <h1>Поиск по объявлениям</h1>
          <p>Найдите потерянных или найденных питомцев в вашем районе</p>
        </div>

        <div className="search-content">
          <aside className="filters-sidebar">
            <div className="filters-title">
              Фильтры <FaFilter />
            </div>
            <Form onSubmit={handleSearch}>
              <div className="filter-group">
                <div className="filter-group-title">Тип животного</div>
                <Form.Control
                  as="select"
                  name="type"
                  value={searchParams.type}
                  onChange={handleInputChange}
                  className="filter-select"
                >
                  <option value="">Выберите тип животного</option>
                  {animalTypes.map(type => (
                    <option key={type.value} value={type.value}>
                      {type.label}
                    </option>
                  ))}
                </Form.Control>
              </div>

              <div className="filter-group">
                <div className="filter-group-title">Статус</div>
                <Form.Control
                  as="select"
                  name="status"
                  value={searchParams.status}
                  onChange={handleInputChange}
                  className="filter-select"
                >
                  <option value="">Все статусы</option>
                  <option value="lost">Потерянные</option>
                  <option value="found">Найденные</option>
                </Form.Control>
              </div>

              <div className="filter-group">
                <div className="filter-group-title">Поиск по тексту</div>
                <Form.Control
                  type="text"
                  name="query"
                  value={searchParams.query}
                  onChange={handleInputChange}
                  placeholder="Введите текст для поиска"
                  className="filter-select"
                />
              </div>

              <Button type="submit" className="search-button" disabled={loading}>
                <FaSearch /> {loading ? 'Поиск...' : 'Найти'}
              </Button>
            </Form>
          </aside>

          <main className="search-results">
            {error && <div className="alert alert-danger mt-4">{error}</div>}

            {loading ? (
              <div className="spinner-border" role="status">
                <span className="visually-hidden">Загрузка...</span>
              </div>
            ) : (
              <div className="results-grid">
                {searchResults.map((ad) => (
                  <div key={ad.id} className="advertisement-card">
                    <div className="card-image-container">
                      <img
                        src={ad.photo || 'https://via.placeholder.com/300x200?text=Нет+фото'}
                        alt={ad.title}
                        className="card-image"
                      />
                      <div className={`status-badge status-${ad.status}`}>
                        {getStatusLabel(ad.status)}
                      </div>
                    </div>
                    <div className="card-body">
                      <h3 className="card-title">{ad.title}</h3>
                      <p className="description">{ad.description}</p>
                      <div className="pet-info">
                        <span className="pet-type">
                          {ad.type}
                        </span>
                      </div>
                      <Button 
                        variant="outline-primary" 
                        onClick={() => handleViewDetails(ad.id)}
                        className="btn-outline-primary"
                      >
                        Подробнее
                      </Button>
                    </div>
                  </div>
                ))}
                {searchResults.length === 0 && !loading && (
                  <div className="no-results">
                    <h3>Объявления не найдены</h3>
                    <p>Попробуйте изменить параметры поиска</p>
                  </div>
                )}
              </div>
            )}
          </main>
        </div>
      </div>
    </>
  );
};

export default SearchByPost;