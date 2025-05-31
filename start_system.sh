#!/bin/bash

echo "🚀 Запуск системы PetFinderVision..."

# Проверяем, что мы в правильной директории
if [ ! -f "manage.py" ]; then
    echo "❌ Ошибка: Запустите скрипт из корневой директории проекта"
    exit 1
fi

# Функция для проверки доступности порта
check_port() {
    local port=$1
    if lsof -Pi :$port -sTCP:LISTEN -t >/dev/null ; then
        echo "⚠️  Порт $port уже занят"
        return 1
    else
        return 0
    fi
}

# Проверяем и запускаем PostgreSQL если нужно
echo "🐘 Проверка базы данных PostgreSQL..."
if ! docker ps | grep -q "postgres:14.5"; then
    echo "🐘 Запуск PostgreSQL через Docker..."
    docker-compose up -d db
    echo "⏳ Ждем запуска базы данных..."
    sleep 5
else
    echo "✅ PostgreSQL уже запущен"
fi

# Проверяем доступность портов
echo "🔍 Проверка портов..."
check_port 8000 || echo "Django сервер уже запущен на порту 8000"
check_port 5004 || echo "ML сервис уже запущен на порту 5004"
check_port 3000 || echo "Frontend уже запущен на порту 3000"

# Активируем виртуальное окружение
echo "🐍 Активация виртуального окружения..."
source venv/bin/activate

# Запуск Django сервера
echo "🐍 Запуск Django сервера (PostgreSQL)..."
python3 manage.py runserver &
DJANGO_PID=$!
echo "Django PID: $DJANGO_PID"

# Ждем запуска Django
sleep 3

# Запуск ML сервиса
echo "🧠 Запуск ML сервиса..."
cd ml_service
python3 app.py &
ML_PID=$!
echo "ML Service PID: $ML_PID"
cd ..

# Ждем запуска ML сервиса
sleep 5

# Обновляем базу векторов признаков
echo "📊 Обновление базы векторов признаков..."
curl -X POST http://localhost:5004/update_database

# Запуск Frontend
echo "⚛️  Запуск Frontend..."
cd frontend
npm start &
FRONTEND_PID=$!
echo "Frontend PID: $FRONTEND_PID"
cd ..

echo ""
echo "✅ Система запущена!"
echo ""
echo "📋 Сервисы:"
echo "   🐘 PostgreSQL: localhost:5432"
echo "   🐍 Django API: http://localhost:8000"
echo "   🧠 ML Service: http://localhost:5004"
echo "   ⚛️  Frontend: http://localhost:3000"
echo ""
echo "👥 Тестовые пользователи:"
echo "   • admin / admin123 (администратор)"
echo "   • testuser / test123 (обычный пользователь)"
echo ""
echo "🔧 Управление:"
echo "   Для остановки всех сервисов: ./stop_system.sh"
echo "   Или нажмите Ctrl+C"
echo ""

# Функция для остановки всех процессов
cleanup() {
    echo ""
    echo "🛑 Остановка системы..."
    kill $DJANGO_PID 2>/dev/null
    kill $ML_PID 2>/dev/null
    kill $FRONTEND_PID 2>/dev/null
    echo "✅ Все сервисы остановлены"
    echo "💡 PostgreSQL продолжает работать в Docker (остановите: docker-compose down)"
    exit 0
}

# Обработка сигнала прерывания
trap cleanup SIGINT SIGTERM

# Ожидание
echo "💡 Нажмите Ctrl+C для остановки всех сервисов"
wait 