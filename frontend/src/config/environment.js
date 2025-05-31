// Конфигурация окружения
const environment = {
  // API URL
  apiUrl: 'http://localhost:8000',
  
  // Другие настройки окружения
  isDevelopment: true,
  isProduction: false,
  
  // Настройки для загрузки файлов
  maxFileSize: 5 * 1024 * 1024, // 5MB в байтах
  allowedFileTypes: ['image/jpeg', 'image/png', 'image/gif'],
  
  // Настройки для карты
  defaultMapCenter: {
    latitude: 55.7558,
    longitude: 37.6173
  },
  defaultMapZoom: 12
};

export default environment; 