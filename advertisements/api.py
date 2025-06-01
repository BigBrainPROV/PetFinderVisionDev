from rest_framework.viewsets import ModelViewSet
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.response import Response
from rest_framework import status
from django.db.models import Q
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.permissions import BasePermission, SAFE_METHODS
import requests
import base64
import json

from advertisements.filters import AdvertisementFilter
from advertisements.models import Advertisement
from advertisements.serializers import (
    AdvertisementRetrieveSerializer,
    AdvertisementCreateSerializer,
    AdvertisementListSerializer,
)


class IsAuthenticatedOrReadOnly(BasePermission):
    """
    Разрешает просмотр всем, но требует аутентификацию для изменения данных
    """
    def has_permission(self, request, view):
        if request.method in SAFE_METHODS:
            return True
        return bool(request.user and request.user.is_authenticated)


class AdvertisementViewSet(ModelViewSet):
    queryset = Advertisement.objects.all()
    filterset_class = AdvertisementFilter
    permission_classes = [IsAuthenticatedOrReadOnly]  # Разрешаем просмотр без аутентификации

    def get_permissions(self):
        """
        Переопределяем получение разрешений в зависимости от действия
        """
        if self.action == 'my_advertisements':
            permission_classes = [IsAuthenticated]
        elif self.action == 'create':
            permission_classes = [AllowAny]  # Разрешаем анонимное создание объявлений
        else:
            permission_classes = [IsAuthenticatedOrReadOnly]
        return [permission() for permission in permission_classes]

    def get_serializer_class(self):
        if self.action == "create":
            return AdvertisementCreateSerializer
        elif self.action == "list":
            return AdvertisementListSerializer
        return AdvertisementRetrieveSerializer

    def create(self, request, *args, **kwargs):
        try:
            print('Received data:', request.data)
            # Добавляем автора объявления
            if request.user.is_authenticated:
                request.data['author'] = request.user.username
            else:
                # Для анонимных пользователей используем указанного автора или "Аноним"
                if 'author' not in request.data or not request.data['author']:
                    request.data['author'] = 'Аноним'
                
            serializer = self.get_serializer(data=request.data)
            if not serializer.is_valid():
                print('Validation errors:', serializer.errors)
                return Response(
                    {'error': 'Validation error', 'details': serializer.errors},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # Создаем объявление
            advertisement = serializer.save()
            
            # Автоматически анализируем фото с помощью ИИ
            if advertisement.photo:
                try:
                    self.analyze_pet_photo(advertisement)
                except Exception as e:
                    print(f'AI analysis failed: {e}')
                    # Продолжаем даже если ИИ анализ не удался
            
            headers = self.get_success_headers(serializer.data)
            return Response(
                serializer.data,
                status=status.HTTP_201_CREATED,
                headers=headers
            )
        except Exception as e:
            print('Error creating advertisement:', str(e))
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )

    def analyze_pet_photo(self, advertisement):
        """Анализирует фото питомца с помощью ML сервиса"""
        try:
            # Читаем изображение
            with open(advertisement.photo.path, 'rb') as image_file:
                image_data = base64.b64encode(image_file.read()).decode('utf-8')
            
            # Отправляем запрос к ML сервису
            ml_response = requests.post(
                'http://localhost:5004/search/',
                json={'image': f'data:image/jpeg;base64,{image_data}'},
                timeout=30
            )
            
            if ml_response.status_code == 200:
                analysis = ml_response.json()
                
                # Обновляем поля на основе анализа ИИ
                if 'animal_type' in analysis:
                    advertisement.type = analysis['animal_type']['label']
                
                if 'color' in analysis:
                    advertisement.color = analysis['color']['label']
                
                if 'eye_color' in analysis:
                    advertisement.eye_color = analysis['eye_color']['label']
                
                if 'face_shape' in analysis:
                    advertisement.face_shape = analysis['face_shape']['label']
                
                if 'special_features' in analysis:
                    advertisement.special_features = analysis['special_features']['label']
                
                # Заполняем новые расширенные поля
                if 'breed_prediction' in analysis:
                    if not advertisement.breed or advertisement.breed == 'Неопределена':
                        advertisement.breed = analysis['breed_prediction']['label']
                
                if 'size_analysis' in analysis:
                    advertisement.size = analysis['size_analysis']['size']
                
                # Определяем тип шерсти на основе анализа
                if 'unique_metrics' in analysis:
                    fluffiness = analysis['unique_metrics'].get('fluffiness', 0)
                    if fluffiness > 0.7:
                        advertisement.coat_type = 'long'
                    elif fluffiness > 0.4:
                        advertisement.coat_type = 'medium'
                    else:
                        advertisement.coat_type = 'short'
                
                # Определяем тип телосложения
                if 'color' in analysis and 'details' in analysis['color']:
                    body_analysis = analysis['color']['details'].get('body_analysis', {})
                    if body_analysis.get('is_elongated'):
                        advertisement.body_type = 'elongated'
                    elif body_analysis.get('is_compact'):
                        advertisement.body_type = 'compact'
                    else:
                        advertisement.body_type = 'normal'
                
                # Сохраняем уникальные метрики
                if 'unique_metrics' in analysis:
                    metrics = analysis['unique_metrics']
                    advertisement.fluffiness_score = metrics.get('fluffiness', 0)
                    advertisement.symmetry_score = metrics.get('symmetry', 0)
                    advertisement.pattern_complexity = metrics.get('pattern_complexity', 0)
                    advertisement.body_proportions = metrics.get('body_proportions', 1.0)
                    advertisement.color_diversity = metrics.get('color_diversity', 1)
                
                # Отмечаем как проанализированное ИИ
                advertisement.ai_analyzed = True
                
                # Вычисляем общую уверенность
                confidences = []
                if 'animal_type' in analysis:
                    confidences.append(analysis['animal_type'].get('confidence', 0))
                if 'color' in analysis:
                    confidences.append(analysis['color'].get('confidence', 0))
                if 'eye_color' in analysis:
                    confidences.append(analysis['eye_color'].get('confidence', 0))
                
                if confidences:
                    advertisement.ai_confidence = sum(confidences) / len(confidences)
                
                advertisement.save()
                print(f'AI analysis completed for advertisement {advertisement.id}')
                
        except Exception as e:
            print(f'Error in AI analysis: {e}')
            # Не прерываем создание объявления если ИИ анализ не удался

    def retrieve(self, request, *args, **kwargs):
        """
        Получение деталей объявления.
        """
        try:
            instance = self.get_object()
            serializer = self.get_serializer(instance)
            return Response(serializer.data)
        except Exception as e:
            print('Error retrieving advertisement:', str(e))
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )

    @action(detail=False, methods=["get"], permission_classes=[IsAuthenticated])
    def my_advertisements(self, request):
        """
        Get advertisements created by the current user.
        """
        try:
            # Удаляем временные объявления этого пользователя
            Advertisement.objects.filter(
                author=request.user.username,
                title="Temporary",
                description="Temporary"
            ).delete()
            
            # Получаем актуальные объявления
            queryset = self.get_queryset().filter(
                author=request.user.username
            ).exclude(
                title="Temporary",
                description="Temporary"
            )
            serializer = self.get_serializer(queryset, many=True)
            return Response(serializer.data)
        except Exception as e:
            print('Error fetching my advertisements:', str(e))
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )

    @action(detail=False, methods=["get"])
    def nearby(self, request):
        """
        Get advertisements near a specific location.
        Required query parameters: latitude, longitude, radius (in kilometers)
        Optional parameters: type, status
        """
        latitude = request.query_params.get('latitude')
        longitude = request.query_params.get('longitude')
        radius = request.query_params.get('radius', 5)  # Default radius: 5km
        
        if not all([latitude, longitude]):
            return Response(
                {"error": "Latitude and longitude are required"},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            latitude = float(latitude)
            longitude = float(longitude)
            radius = float(radius)
        except ValueError:
            return Response(
                {"error": "Invalid coordinates or radius"},
                status=status.HTTP_400_BAD_REQUEST
            )

        queryset = self.get_queryset()
        
        # Apply type filter if provided
        ad_type = request.query_params.get('type')
        if ad_type and ad_type != 'all':
            queryset = queryset.filter(type=ad_type)
            
        # Apply status filter if provided
        ad_status = request.query_params.get('status')
        if ad_status:
            queryset = queryset.filter(status=ad_status)

        # Apply radius filter
        filtered_queryset = self.filterset_class({'latitude': latitude, 'longitude': longitude, 'radius': radius}, queryset=queryset).qs
        
        serializer = self.get_serializer(filtered_queryset, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=["get"])
    def search(self, request):
        """
        Search advertisements by various criteria including animal characteristics.
        """
        try:
            query = request.query_params.get('q', '')
            ad_type = request.query_params.get('type')
            status_param = request.query_params.get('status')
            color = request.query_params.get('color')
            eye_color = request.query_params.get('eye_color')
            face_shape = request.query_params.get('face_shape')
            special_features = request.query_params.get('special_features')
            
            # Новые параметры поиска
            size = request.query_params.get('size')
            coat_type = request.query_params.get('coat_type')
            body_type = request.query_params.get('body_type')
            breed = request.query_params.get('breed')

            queryset = self.get_queryset()

            # Базовый текстовый поиск
            if query:
                queryset = queryset.filter(
                    Q(title__icontains=query) |
                    Q(description__icontains=query) |
                    Q(breed__icontains=query) |
                    Q(location__icontains=query)
                )

            # Фильтрация по характеристикам
            filters = {}
            
            if ad_type and ad_type != 'all':
                filters['type'] = ad_type
                
            if status_param:
                filters['status'] = status_param
                
            if color:
                filters['color'] = color
                
            if eye_color:
                filters['eye_color'] = eye_color
                
            if face_shape:
                filters['face_shape'] = face_shape
                
            if special_features and special_features != 'none':
                filters['special_features'] = special_features
            
            # Новые фильтры
            if size:
                filters['size'] = size
                
            if coat_type:
                filters['coat_type'] = coat_type
                
            if body_type:
                filters['body_type'] = body_type
                
            # УЛУЧШЕННЫЙ поиск по породе
            if breed:
                # Поиск по точному совпадению или частичному совпадению
                breed_filter = Q(breed__iexact=breed) | Q(breed__icontains=breed)
                
                # Дополнительные варианты поиска для популярных пород
                breed_lower = breed.lower()
                if 'лабрадор' in breed_lower:
                    breed_filter |= Q(breed__icontains='лабрадор')
                elif 'овчарка' in breed_lower:
                    breed_filter |= Q(breed__icontains='овчарка')
                elif 'хаски' in breed_lower:
                    breed_filter |= Q(breed__icontains='хаски') | Q(breed__icontains='сибирский')
                elif 'такса' in breed_lower:
                    breed_filter |= Q(breed__icontains='такса')
                elif 'ретривер' in breed_lower:
                    breed_filter |= Q(breed__icontains='ретривер')
                elif 'бульдог' in breed_lower:
                    breed_filter |= Q(breed__icontains='бульдог')
                elif 'спаниель' in breed_lower:
                    breed_filter |= Q(breed__icontains='спаниель')
                elif 'терьер' in breed_lower:
                    breed_filter |= Q(breed__icontains='терьер')
                elif 'персидская' in breed_lower:
                    breed_filter |= Q(breed__icontains='персидская')
                elif 'сиамская' in breed_lower:
                    breed_filter |= Q(breed__icontains='сиамская')
                elif 'британская' in breed_lower:
                    breed_filter |= Q(breed__icontains='британская')
                elif 'мейн' in breed_lower or 'кун' in breed_lower:
                    breed_filter |= Q(breed__icontains='мейн-кун')
                
                queryset = queryset.filter(breed_filter)

            # Применяем остальные фильтры
            if filters:
                queryset = queryset.filter(**filters)

            # Исключаем временные объявления
            queryset = queryset.exclude(
                title="Temporary",
                description="Temporary"
            )

            serializer = self.get_serializer(queryset, many=True)
            return Response(serializer.data)
        except Exception as e:
            print('Error searching advertisements:', str(e))
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )

    @action(detail=False, methods=["post"], permission_classes=[AllowAny])
    def analyze_photo(self, request):
        """
        Анализирует фото питомца с помощью ИИ и возвращает похожие объявления
        """
        try:
            if 'image' not in request.data:
                return Response(
                    {"error": "No image provided"},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            image_data = request.data['image']
            
            # Отправляем запрос к ML сервису
            ml_response = requests.post(
                'http://localhost:5004/search/',
                json={'image': image_data},
                timeout=30
            )
            
            if ml_response.status_code != 200:
                return Response(
                    {"error": "ML service error"},
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR
                )
            
            analysis = ml_response.json()
            
            # Получаем похожие объявления из ML сервиса
            similar_pets = analysis.get('similar_pets', [])
            
            # УЛУЧШЕННЫЙ поиск в базе данных по характеристикам
            queryset = Advertisement.objects.all()
            
            # Фильтруем по типу животного
            animal_type_filter = None
            if 'animal_type' in analysis:
                animal_type = analysis['animal_type']['label']
                animal_type_filter = Q(type=animal_type)
                queryset = queryset.filter(animal_type_filter)
            
            # НОВЫЙ: Фильтруем по породе (приоритетный поиск)
            breed_matches = []
            if 'breed_prediction' in analysis:
                predicted_breed = analysis['breed_prediction']['label']
                breed_confidence = analysis['breed_prediction']['confidence']
                
                print(f"Predicted breed: {predicted_breed} with confidence {breed_confidence}")
                
                # Если уверенность в породе высокая, ищем точные совпадения
                if breed_confidence > 0.7 and predicted_breed != 'Смешанная порода' and predicted_breed != 'Домашняя короткошерстная':
                    breed_query = Q(breed__iexact=predicted_breed) | Q(breed__icontains=predicted_breed)
                    
                    # Дополнительные варианты поиска
                    breed_lower = predicted_breed.lower()
                    if 'лабрадор' in breed_lower:
                        breed_query |= Q(breed__icontains='лабрадор')
                    elif 'овчарка' in breed_lower:
                        breed_query |= Q(breed__icontains='овчарка')
                    elif 'хаски' in breed_lower or 'сибирский' in breed_lower:
                        breed_query |= Q(breed__icontains='хаски') | Q(breed__icontains='сибирский')
                    elif 'ретривер' in breed_lower:
                        breed_query |= Q(breed__icontains='ретривер')
                    elif 'такса' in breed_lower:
                        breed_query |= Q(breed__icontains='такса')
                    elif 'бульдог' in breed_lower:
                        breed_query |= Q(breed__icontains='бульдог')
                    elif 'спаниель' in breed_lower:
                        breed_query |= Q(breed__icontains='спаниель')
                    elif 'терьер' in breed_lower:
                        breed_query |= Q(breed__icontains='терьер')
                    elif 'персидская' in breed_lower:
                        breed_query |= Q(breed__icontains='персидская')
                    elif 'сиамская' in breed_lower:
                        breed_query |= Q(breed__icontains='сиамская')
                    elif 'британская' in breed_lower:
                        breed_query |= Q(breed__icontains='британская')
                    elif 'мейн' in breed_lower or 'кун' in breed_lower:
                        breed_query |= Q(breed__icontains='мейн-кун')
                    
                    # Применяем фильтр по типу животного если есть
                    if animal_type_filter:
                        breed_matches = Advertisement.objects.filter(animal_type_filter & breed_query).exclude(
                            title="Temporary", description="Temporary"
                        )[:10]
                    else:
                        breed_matches = Advertisement.objects.filter(breed_query).exclude(
                            title="Temporary", description="Temporary"
                        )[:10]
                    
                    print(f"Found {len(breed_matches)} breed matches for {predicted_breed}")
            
            # Фильтруем по цвету (вторичный поиск)
            color_matches = []
            if 'color' in analysis:
                color = analysis['color']['label']
                color_query = Q(color=color)
                
                # Применяем фильтр по типу животного если есть
                if animal_type_filter:
                    color_matches = Advertisement.objects.filter(animal_type_filter & color_query).exclude(
                        title="Temporary", description="Temporary"
                    )[:10]
                else:
                    color_matches = Advertisement.objects.filter(color_query).exclude(
                        title="Temporary", description="Temporary"
                    )[:10]
            
            # Общий поиск по типу животного (если не нашли по породе и цвету)
            general_matches = []
            if animal_type_filter:
                general_matches = Advertisement.objects.filter(animal_type_filter).exclude(
                    title="Temporary", description="Temporary"
                )[:5]
            
            # Объединяем результаты ML сервиса с результатами из БД
            combined_results = []
            
            # ИСПРАВЛЕНИЕ: Фильтруем результаты ML сервиса по типу животного
            filtered_similar_pets = []
            if 'animal_type' in analysis:
                detected_type = analysis['animal_type']['label']
                print(f"Detected animal type: {detected_type}")
                
                for pet in similar_pets:
                    try:
                        advertisement = Advertisement.objects.get(id=pet.get('ad_id'))
                        # КРИТИЧЕСКОЕ ИСПРАВЛЕНИЕ: Показываем только животных того же типа
                        if advertisement.type == detected_type:
                            filtered_similar_pets.append(pet)
                            print(f"Added similar pet: {advertisement.title} (type: {advertisement.type})")
                        else:
                            print(f"Filtered out pet: {advertisement.title} (type: {advertisement.type}, expected: {detected_type})")
                    except Advertisement.DoesNotExist:
                        continue
            else:
                filtered_similar_pets = similar_pets
            
            # Добавляем ОТФИЛЬТРОВАННЫЕ результаты из ML сервиса (высший приоритет)
            for pet in filtered_similar_pets:
                ad_id = pet.get('ad_id')
                try:
                    advertisement = Advertisement.objects.get(id=ad_id)
                    ad_serializer = AdvertisementListSerializer(advertisement)
                    ad_data = ad_serializer.data
                    ad_data['similarity'] = pet.get('similarity', 0)
                    ad_data['match_type'] = 'visual_similarity'
                    combined_results.append(ad_data)
                except Advertisement.DoesNotExist:
                    continue
            
            # Добавляем совпадения по породе (высокий приоритет)
            existing_ids = {result.get('id') for result in combined_results}
            for ad in breed_matches:
                if ad.id not in existing_ids:
                    ad_serializer = AdvertisementListSerializer(ad)
                    ad_data = ad_serializer.data
                    ad_data['similarity'] = 0.85  # Высокое сходство для совпадений по породе
                    ad_data['match_type'] = 'breed_match'
                    combined_results.append(ad_data)
                    existing_ids.add(ad.id)
            
            # Добавляем совпадения по цвету (средний приоритет)
            for ad in color_matches:
                if ad.id not in existing_ids:
                    ad_serializer = AdvertisementListSerializer(ad)
                    ad_data = ad_serializer.data
                    ad_data['similarity'] = 0.6  # Среднее сходство для совпадений по цвету
                    ad_data['match_type'] = 'color_match'
                    combined_results.append(ad_data)
                    existing_ids.add(ad.id)
            
            # Добавляем общие совпадения по типу животного (низкий приоритет)
            for ad in general_matches:
                if ad.id not in existing_ids:
                    ad_serializer = AdvertisementListSerializer(ad)
                    ad_data = ad_serializer.data
                    ad_data['similarity'] = 0.4  # Базовое сходство для совпадений по типу
                    ad_data['match_type'] = 'type_match'
                    combined_results.append(ad_data)
                    existing_ids.add(ad.id)
            
            # Сортируем по убыванию сходства
            combined_results.sort(key=lambda x: x.get('similarity', 0), reverse=True)
            
            return Response({
                'analysis': analysis,
                'similar_pets': combined_results[:15],  # Возвращаем топ 15 результатов
                'total_found': len(combined_results)
            })
            
        except Exception as e:
            print('Error in photo analysis:', str(e))
            return Response(
                {'error': str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    @action(detail=True, methods=["post"])
    def reanalyze(self, request, pk=None):
        """
        Повторно анализирует фото существующего объявления
        """
        try:
            advertisement = self.get_object()
            
            if not advertisement.photo:
                return Response(
                    {"error": "No photo to analyze"},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # Выполняем анализ
            self.analyze_pet_photo(advertisement)
            
            # Возвращаем обновленные данные
            serializer = self.get_serializer(advertisement)
            return Response({
                'message': 'Photo reanalyzed successfully',
                'advertisement': serializer.data
            })
            
        except Exception as e:
            print('Error in reanalysis:', str(e))
            return Response(
                {'error': str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    @action(detail=False, methods=["post"])
    def upload_photos(self, request):
        """
        Upload photos for an advertisement.
        """
        try:
            photos = request.FILES.getlist('photos')
            if not photos:
                return Response(
                    {"error": "No photos provided"},
                    status=status.HTTP_400_BAD_REQUEST
                )

            uploaded_urls = []
            for photo in photos:
                # Создаем временный путь для фотографии
                temp_ad = Advertisement.objects.create(
                    title="Temporary",
                    description="Temporary",
                    author=request.user.username if request.user.is_authenticated else "Anonymous",
                    photo=photo,
                    breed="Temporary",
                    color="white",
                    sex="unknown",
                    type="cat",
                    eye_color="yellow",
                    face_shape="round",
                    special_features="none",
                    status="lost"
                )
                uploaded_urls.append(request.build_absolute_uri(temp_ad.photo.url))

            return Response({"urls": uploaded_urls}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response(
                {"error": str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


@api_view(['POST'])
@permission_classes([AllowAny])
def analyze_photo_standalone(request):
    """
    Отдельный view для анализа фото питомца с помощью ИИ
    """
    try:
        print(f"Received request data keys: {list(request.data.keys())}")
        
        if 'image' not in request.data:
            return Response(
                {"error": "No image provided"},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        image_data = request.data['image']
        print(f"Image data type: {type(image_data)}")
        print(f"Image data length: {len(str(image_data)) if image_data else 0}")
        
        # Проверяем, что image_data не пустой
        if not image_data:
            return Response(
                {"error": "Empty image data provided"},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # ИСПРАВЛЕНИЕ: Валидация и очистка данных изображения
        if isinstance(image_data, str):
            # Если это data URL, извлекаем только base64 часть
            if image_data.startswith('data:image'):
                if ',' in image_data:
                    image_data = image_data.split(',', 1)[1]
                else:
                    return Response(
                        {"error": "Invalid data URL format"},
                        status=status.HTTP_400_BAD_REQUEST
                    )
            
            # Проверяем, что это валидный base64
            try:
                import base64
                base64.b64decode(image_data)
            except Exception as e:
                return Response(
                    {"error": f"Invalid base64 data: {str(e)}"},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # Восстанавливаем data URL для ML сервиса
            if not image_data.startswith('data:image'):
                image_data = f"data:image/jpeg;base64,{image_data}"
        
        print("Image data validation passed")
        
        # Отправляем запрос к ML сервису
        print("Sending request to ML service...")
        try:
            ml_response = requests.post(
                'http://localhost:5004/search/',
                json={'image': image_data},
                timeout=60  # Увеличиваем таймаут
            )
        except requests.exceptions.Timeout:
            return Response(
                {"error": "ML service timeout - image processing took too long"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
        except requests.exceptions.ConnectionError:
            return Response(
                {"error": "ML service unavailable"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
        
        print(f"ML service response status: {ml_response.status_code}")
        
        if ml_response.status_code != 200:
            error_text = ml_response.text
            print(f"ML service error response: {error_text}")
            
            # Возвращаем более понятную ошибку пользователю
            if "cannot identify image file" in error_text:
                return Response(
                    {"error": "Не удалось распознать изображение. Пожалуйста, загрузите корректное изображение в формате JPEG или PNG."},
                    status=status.HTTP_400_BAD_REQUEST
                )
            elif "Incorrect padding" in error_text:
                return Response(
                    {"error": "Поврежденное изображение. Пожалуйста, попробуйте загрузить другое изображение."},
                    status=status.HTTP_400_BAD_REQUEST
                )
            else:
                return Response(
                    {"error": "Ошибка обработки изображения. Попробуйте позже."},
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR
                )
        
        analysis = ml_response.json()
        print("ML service analysis completed successfully")
        
        # Получаем похожие объявления из ML сервиса
        similar_pets = analysis.get('similar_pets', [])
        
        # УЛУЧШЕННЫЙ поиск в базе данных по характеристикам
        queryset = Advertisement.objects.all()
        
        # Фильтруем по типу животного
        animal_type_filter = None
        if 'animal_type' in analysis:
            animal_type = analysis['animal_type']['label']
            animal_type_filter = Q(type=animal_type)
            queryset = queryset.filter(animal_type_filter)
        
        # НОВЫЙ: Фильтруем по породе (приоритетный поиск)
        breed_matches = []
        if 'breed_prediction' in analysis:
            predicted_breed = analysis['breed_prediction']['label']
            breed_confidence = analysis['breed_prediction']['confidence']
            
            print(f"Predicted breed: {predicted_breed} with confidence {breed_confidence}")
            
            # Если уверенность в породе высокая, ищем точные совпадения
            if breed_confidence > 0.7 and predicted_breed != 'Смешанная порода' and predicted_breed != 'Домашняя короткошерстная':
                breed_query = Q(breed__iexact=predicted_breed) | Q(breed__icontains=predicted_breed)
                
                # Дополнительные варианты поиска
                breed_lower = predicted_breed.lower()
                if 'лабрадор' in breed_lower:
                    breed_query |= Q(breed__icontains='лабрадор')
                elif 'овчарка' in breed_lower:
                    breed_query |= Q(breed__icontains='овчарка')
                elif 'хаски' in breed_lower or 'сибирский' in breed_lower:
                    breed_query |= Q(breed__icontains='хаски') | Q(breed__icontains='сибирский')
                elif 'ретривер' in breed_lower:
                    breed_query |= Q(breed__icontains='ретривер')
                elif 'такса' in breed_lower:
                    breed_query |= Q(breed__icontains='такса')
                elif 'бульдог' in breed_lower:
                    breed_query |= Q(breed__icontains='бульдог')
                elif 'спаниель' in breed_lower:
                    breed_query |= Q(breed__icontains='спаниель')
                elif 'терьер' in breed_lower:
                    breed_query |= Q(breed__icontains='терьер')
                elif 'персидская' in breed_lower:
                    breed_query |= Q(breed__icontains='персидская')
                elif 'сиамская' in breed_lower:
                    breed_query |= Q(breed__icontains='сиамская')
                elif 'британская' in breed_lower:
                    breed_query |= Q(breed__icontains='британская')
                elif 'мейн' in breed_lower or 'кун' in breed_lower:
                    breed_query |= Q(breed__icontains='мейн-кун')
                
                # Применяем фильтр по типу животного если есть
                if animal_type_filter:
                    breed_matches = Advertisement.objects.filter(animal_type_filter & breed_query).exclude(
                        title="Temporary", description="Temporary"
                    )[:10]
                else:
                    breed_matches = Advertisement.objects.filter(breed_query).exclude(
                        title="Temporary", description="Temporary"
                    )[:10]
                
                print(f"Found {len(breed_matches)} breed matches for {predicted_breed}")
        
        # Фильтруем по цвету (вторичный поиск)
        color_matches = []
        if 'color' in analysis:
            color = analysis['color']['label']
            color_query = Q(color=color)
            
            # Применяем фильтр по типу животного если есть
            if animal_type_filter:
                color_matches = Advertisement.objects.filter(animal_type_filter & color_query).exclude(
                    title="Temporary", description="Temporary"
                )[:10]
            else:
                color_matches = Advertisement.objects.filter(color_query).exclude(
                    title="Temporary", description="Temporary"
                )[:10]
        
        # Общий поиск по типу животного (если не нашли по породе и цвету)
        general_matches = []
        if animal_type_filter:
            general_matches = Advertisement.objects.filter(animal_type_filter).exclude(
                title="Temporary", description="Temporary"
            )[:5]
        
        # Объединяем результаты ML сервиса с результатами из БД
        combined_results = []
        
        # ИСПРАВЛЕНИЕ: Фильтруем результаты ML сервиса по типу животного
        filtered_similar_pets = []
        if 'animal_type' in analysis:
            detected_type = analysis['animal_type']['label']
            print(f"Detected animal type: {detected_type}")
            
            for pet in similar_pets:
                try:
                    advertisement = Advertisement.objects.get(id=pet.get('ad_id'))
                    # КРИТИЧЕСКОЕ ИСПРАВЛЕНИЕ: Показываем только животных того же типа
                    if advertisement.type == detected_type:
                        filtered_similar_pets.append(pet)
                        print(f"Added similar pet: {advertisement.title} (type: {advertisement.type})")
                    else:
                        print(f"Filtered out pet: {advertisement.title} (type: {advertisement.type}, expected: {detected_type})")
                except Advertisement.DoesNotExist:
                    continue
        else:
            filtered_similar_pets = similar_pets
        
        # Добавляем ОТФИЛЬТРОВАННЫЕ результаты из ML сервиса (высший приоритет)
        for pet in filtered_similar_pets:
            ad_id = pet.get('ad_id')
            try:
                advertisement = Advertisement.objects.get(id=ad_id)
                ad_serializer = AdvertisementListSerializer(advertisement)
                ad_data = ad_serializer.data
                ad_data['similarity'] = pet.get('similarity', 0)
                ad_data['match_type'] = 'visual_similarity'
                combined_results.append(ad_data)
            except Advertisement.DoesNotExist:
                continue
        
        # Добавляем совпадения по породе (высокий приоритет)
        existing_ids = {result.get('id') for result in combined_results}
        for ad in breed_matches:
            if ad.id not in existing_ids:
                ad_serializer = AdvertisementListSerializer(ad)
                ad_data = ad_serializer.data
                ad_data['similarity'] = 0.85  # Высокое сходство для совпадений по породе
                ad_data['match_type'] = 'breed_match'
                combined_results.append(ad_data)
                existing_ids.add(ad.id)
        
        # Добавляем совпадения по цвету (средний приоритет)
        for ad in color_matches:
            if ad.id not in existing_ids:
                ad_serializer = AdvertisementListSerializer(ad)
                ad_data = ad_serializer.data
                ad_data['similarity'] = 0.6  # Среднее сходство для совпадений по цвету
                ad_data['match_type'] = 'color_match'
                combined_results.append(ad_data)
                existing_ids.add(ad.id)
        
        # Добавляем общие совпадения по типу животного (низкий приоритет)
        for ad in general_matches:
            if ad.id not in existing_ids:
                ad_serializer = AdvertisementListSerializer(ad)
                ad_data = ad_serializer.data
                ad_data['similarity'] = 0.4  # Базовое сходство для совпадений по типу
                ad_data['match_type'] = 'type_match'
                combined_results.append(ad_data)
                existing_ids.add(ad.id)
        
        # Сортируем по убыванию сходства
        combined_results.sort(key=lambda x: x.get('similarity', 0), reverse=True)
        
        return Response({
            'analysis': analysis,
            'similar_pets': combined_results[:15],  # Возвращаем топ 15 результатов
            'total_found': len(combined_results)
        })
        
    except Exception as e:
        print(f'Error in photo analysis: {str(e)}')
        import traceback
        print(f'Traceback: {traceback.format_exc()}')
        return Response(
            {'error': 'Произошла внутренняя ошибка сервера. Попробуйте позже.'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )
