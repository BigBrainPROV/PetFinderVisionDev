# Используем официальный Python образ
FROM python:3.9-slim

# Устанавливаем системные зависимости
RUN apt-get update && apt-get install -y \
    postgresql-client \
    libpq-dev \
    gcc \
    python3-dev \
    libpng-dev \
    libjpeg-dev \
    libfreetype6-dev \
    liblcms2-dev \
    libwebp-dev \
    tcl8.6-dev \
    tk8.6-dev \
    python3-tk \
    libharfbuzz-dev \
    libfribidi-dev \
    libxcb1-dev \
    && rm -rf /var/lib/apt/lists/*

# Устанавливаем рабочую директорию
WORKDIR /app

# Копируем requirements.txt
COPY requirements.txt .

# Устанавливаем Python зависимости
RUN pip install --no-cache-dir -r requirements.txt

# Устанавливаем дополнительные зависимости Django
RUN pip install \
    Django==4.2 \
    djangorestframework==3.14.0 \
    djangorestframework-simplejwt==5.2.2 \
    django-filter==23.2 \
    django-cors-headers \
    httpx==0.24.1

# Копируем исходный код проекта
COPY . .

# Создаем директории для медиа и статических файлов
RUN mkdir -p /app/media /app/static

# Устанавливаем права доступа
RUN chmod +x manage.py

# Экспонируем порт
EXPOSE 8000

# Команда по умолчанию
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"] 