# PetFinderVision

Система поиска потерянных питомцев.

## Запуск

```bash
# Установка зависимостей
pip install -r requirements.txt
cd frontend && npm install && cd ..

# Миграции базы данных
python manage.py migrate

# Запуск всех сервисов
./start_system.sh
```

## Адреса

- Frontend: http://localhost:3000
- Backend API: http://localhost:8000
- ML Service: http://localhost:5004

## Компоненты

- **Django** - Backend API и админка
- **React** - Frontend интерфейс  
- **Flask** - ML сервис для анализа изображений
