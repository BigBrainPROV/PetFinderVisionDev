from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.parsers import MultiPartParser, FormParser
from django.conf import settings
from .services.clip_service import CLIPService
import os
import logging

logger = logging.getLogger(__name__)

class SimilaritySearchView(APIView):
    parser_classes = (MultiPartParser, FormParser)
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.clip_service = CLIPService()
        self.clip_service.build_index()
    
    def get(self, request):
        """Проверка доступности сервиса"""
        return Response({
            'status': 'ok',
            'message': 'Сервис поиска похожих животных доступен'
        })
    
    def post(self, request):
        try:
            # Проверяем наличие файла в запросе
            if 'file' in request.FILES:
                file = request.FILES['file']
                logger.info(f"Получен файл: {file.name}, размер: {file.size} байт")
                
                # Читаем содержимое файла
                file_content = file.read()
                
                # Выполняем поиск
                results = self.clip_service.search(file_content)
                
                # Формируем ответ
                response_data = []
                for ad, similarity in results:
                    if similarity < 0.75:
                        continue
                    response_data.append({
                        'id': ad.id,
                        'title': ad.title,
                        'description': ad.description,
                        'photo_url': request.build_absolute_uri(ad.photo.url) if ad.photo else None,
                        'breed': ad.breed,
                        'color': ad.color,
                        'type': ad.type,
                        'similarity_score': similarity
                    })
                
                return Response(response_data)
            else:
                return Response(
                    {'error': 'Файл не найден в запросе'},
                    status=status.HTTP_400_BAD_REQUEST
                )
                
        except Exception as e:
            logger.error(f"Ошибка при поиске похожих животных: {str(e)}")
            return Response(
                {'error': str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            ) 