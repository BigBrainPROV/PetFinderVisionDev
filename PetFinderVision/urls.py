"""PetFinderVision URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.conf import settings
from django.conf.urls.static import static
from django.urls import include, path, re_path
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from django.views.generic import TemplateView
import httpx
from django.http import HttpResponse, JsonResponse
from rest_framework.decorators import api_view, parser_classes
from rest_framework.parsers import MultiPartParser, FormParser
import json
from django.views.static import serve
import logging
import tempfile
import os
import asyncio
from advertisements.models import Advertisement
import traceback

logger = logging.getLogger(__name__)

from PetFinderVision.router import router

# Добавляем view для проксирования запросов к сервису поиска
@api_view(['POST'])
@parser_classes([MultiPartParser, FormParser])
def search_proxy(request):
    logger.info("Получен запрос на поиск")
    try:
        # Проверяем наличие файла в запросе
        if 'file' not in request.FILES and 'image' not in request.FILES:
            logger.error("Файл не найден в запросе")
            return JsonResponse({'error': 'Файл не найден в запросе'}, status=400)

        # Получаем файл из запроса
        image_file = request.FILES.get('file') or request.FILES.get('image')
        
        # Создаем временный файл для сохранения изображения
        with tempfile.NamedTemporaryFile(delete=False) as temp_file:
            for chunk in image_file.chunks():
                temp_file.write(chunk)
            temp_file_path = temp_file.name

        logger.info(f"Сохранен временный файл: {temp_file_path}")

        try:
            # Отправляем запрос в сервис поиска
            with open(temp_file_path, 'rb') as f:
                files = {'file': (image_file.name, f, image_file.content_type)}
                response = httpx.post('http://localhost:5001/predict', files=files, timeout=30.0)
                
            logger.info(f"Получен ответ от сервиса поиска: {response.status_code}")
            logger.info(f"Тело ответа: {response.text}")

            if response.status_code == 200:
                predictions = response.json()
                logger.info(f"Получены предсказания: {predictions}")
                
                similar_pets = []
                
                # Получаем тип животного из предсказаний
                if 'animal_type' in predictions:
                    animal_label = predictions['animal_type'].get('label')
                    confidence = predictions['animal_type'].get('confidence', 0)
                    
                    logger.info(f"Определен тип животного: {animal_label} с уверенностью {confidence}")
                    
                    if animal_label:
                        # Преобразуем метку в формат базы данных
                        db_animal_type = {
                            'cat': 'cat',
                            'dog': 'dog',
                            'bird': 'bird',
                            'rodent': 'rodent',
                            'rabbit': 'rabbit',
                            'reptile': 'reptile'
                        }.get(animal_label.lower(), 'other')
                        
                        # Ищем похожих питомцев
                        pets = Advertisement.objects.filter(type=db_animal_type)
                        
                        # Добавляем дополнительные фильтры на основе предсказаний
                        if 'color' in predictions:
                            color_label = predictions['color'].get('label')
                            if color_label:
                                pets = pets.filter(color=color_label.lower())
                        
                        if 'eye_color' in predictions:
                            eye_color_label = predictions['eye_color'].get('label')
                            if eye_color_label:
                                pets = pets.filter(eye_color=eye_color_label.lower())
                        
                        if 'face_shape' in predictions:
                            face_shape_label = predictions['face_shape'].get('label')
                            if face_shape_label:
                                pets = pets.filter(face_shape=face_shape_label.lower())
                        
                        # Ограничиваем количество результатов
                        pets = pets[:5]
                        logger.info(f"Найдено {len(pets)} похожих питомцев типа {db_animal_type}")
                        
                        for pet in pets:
                            try:
                                photo_url = request.build_absolute_uri(pet.photo.url) if pet.photo else None
                                similar_pets.append({
                                    'id': pet.id,
                                    'title': pet.title,
                                    'description': pet.description,
                                    'photo': photo_url,
                                    'breed': pet.breed,
                                    'color': pet.color,
                                    'eye_color': pet.eye_color,
                                    'face_shape': pet.face_shape,
                                    'special_features': pet.special_features,
                                    'similarity': round(confidence * 100, 1)
                                })
                            except Exception as e:
                                logger.error(f"Ошибка при обработке питомца {pet.id}: {str(e)}")
                                continue
                
                return JsonResponse({'results': similar_pets})
            else:
                logger.error(f"Ошибка от сервиса поиска: {response.status_code} - {response.text}")
                return JsonResponse(
                    {'error': 'Ошибка при обработке изображения'},
                    status=500
                )
                
        except Exception as e:
            logger.error(f"Ошибка при отправке запроса в сервис поиска: {str(e)}")
            return JsonResponse(
                {'error': 'Ошибка при обработке запроса'},
                status=500
            )
            
        finally:
            # Удаляем временный файл
            try:
                os.unlink(temp_file_path)
            except Exception as e:
                logger.error(f"Ошибка при удалении временного файла: {str(e)}")
                
    except Exception as e:
        logger.error(f"Общая ошибка: {str(e)}\n{traceback.format_exc()}")
        return JsonResponse(
            {'error': 'Внутренняя ошибка сервера'},
            status=500
        )

urlpatterns = [
    path("admin/", admin.site.urls),
    path("api-auth/", include("rest_framework.urls")),
    path("api/", include(router.urls)),
    path("api/", include('advertisements.urls')),
    path("api/", include('user_register.urls')),
    path("api/token/", TokenObtainPairView.as_view(), name="token_obtain_pair"),
    path("api/token/refresh/", TokenRefreshView.as_view(), name="token_refresh"),
    path("api/search/", search_proxy, name="search_proxy"),
    re_path(r'^uploads/(?P<path>.*)$', serve, {
        'document_root': settings.MEDIA_ROOT,
    }),
]

if settings.DEBUG is True:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
