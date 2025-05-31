#!/usr/bin/env python3
"""
🆓 Бесплатные API для анализа животных в PetFinderVision

Включает:
- Hugging Face Inference API (бесплатно)
- Локальные YOLO модели (offline)
- Гибридный анализатор
"""

import os
import io
import asyncio
import aiohttp
import requests
import logging
from typing import Dict, List, Optional, Any
from PIL import Image
import numpy as np

# Настройка логирования
logger = logging.getLogger(__name__)

class HuggingFaceVisionAPI:
    """Hugging Face API для анализа животных"""
    
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.headers = {"Authorization": f"Bearer {api_key}"}
        self.base_url = "https://api-inference.huggingface.co/models"
        
        # Модели для разных задач
        self.models = {
            'classification': 'microsoft/resnet-50',
            'detection': 'facebook/detr-resnet-50',
            'animal_specific': 'google/vit-base-patch16-224-in21k'
        }
        
    async def analyze_image(self, image_data: bytes) -> Dict[str, Any]:
        """Анализ изображения через Hugging Face"""
        try:
            logger.info("Starting Hugging Face analysis...")
            
            # Параллельно запускаем несколько моделей
            tasks = [
                self._classify_image(image_data),
                self._detect_objects(image_data)
            ]
            
            classification_result, detection_result = await asyncio.gather(*tasks, return_exceptions=True)
            
            # Обрабатываем результаты
            if isinstance(classification_result, Exception):
                logger.warning(f"Classification failed: {classification_result}")
                classification_result = []
            
            if isinstance(detection_result, Exception):
                logger.warning(f"Detection failed: {detection_result}")
                detection_result = []
            
            return self._process_hf_results(classification_result, detection_result)
            
        except Exception as e:
            logger.error(f"Error calling Hugging Face API: {e}")
            return {}
    
    async def _classify_image(self, image_data: bytes) -> List[Dict]:
        """Классификация изображения"""
        url = f"{self.base_url}/{self.models['classification']}"
        
        try:
            async with aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=30)) as session:
                async with session.post(url, headers=self.headers, data=image_data) as response:
                    if response.status == 200:
                        result = await response.json()
                        logger.info(f"Classification completed: {len(result)} results")
                        return result
                    else:
                        logger.warning(f"Classification API returned status {response.status}")
                        return []
        except Exception as e:
            logger.error(f"Classification request failed: {e}")
            return []
    
    async def _detect_objects(self, image_data: bytes) -> List[Dict]:
        """Детекция объектов"""
        url = f"{self.base_url}/{self.models['detection']}"
        
        try:
            async with aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=30)) as session:
                async with session.post(url, headers=self.headers, data=image_data) as response:
                    if response.status == 200:
                        result = await response.json()
                        logger.info(f"Object detection completed: {len(result)} objects")
                        return result
                    else:
                        logger.warning(f"Detection API returned status {response.status}")
                        return []
        except Exception as e:
            logger.error(f"Detection request failed: {e}")
            return []
    
    def _process_hf_results(self, classification: List[Dict], detection: List[Dict]) -> Dict[str, Any]:
        """Обработка результатов Hugging Face"""
        processed = {
            'animals_detected': [],
            'classifications': classification,
            'objects': detection,
            'confidence': 0.0,
            'source': 'huggingface'
        }
        
        # Ключевые слова для животных
        animal_keywords = [
            'dog', 'cat', 'bird', 'animal', 'pet', 'canine', 'feline',
            'puppy', 'kitten', 'retriever', 'shepherd', 'terrier',
            'siamese', 'persian', 'bulldog', 'labrador', 'beagle'
        ]
        
        # Анализируем классификацию
        for item in classification:
            if not isinstance(item, dict):
                continue
                
            label = item.get('label', '').lower()
            score = item.get('score', 0)
            
            if any(keyword in label for keyword in animal_keywords):
                # Определяем тип животного
                animal_type = self._determine_animal_type(label)
                
                processed['animals_detected'].append({
                    'type': animal_type,
                    'confidence': score,
                    'label': item.get('label', ''),
                    'breed_info': self._extract_breed_info(label)
                })
                processed['confidence'] = max(processed['confidence'], score)
        
        # Анализируем детекцию объектов
        for obj in detection:
            if not isinstance(obj, dict):
                continue
                
            label = obj.get('label', '').lower()
            score = obj.get('score', 0)
            
            if any(keyword in label for keyword in animal_keywords) and score > 0.3:
                animal_type = self._determine_animal_type(label)
                
                processed['animals_detected'].append({
                    'type': animal_type,
                    'confidence': score,
                    'label': obj.get('label', ''),
                    'bbox': obj.get('box', {}),
                    'source': 'detection'
                })
                processed['confidence'] = max(processed['confidence'], score)
        
        # Удаляем дубликаты и сортируем по уверенности
        processed['animals_detected'] = self._deduplicate_animals(processed['animals_detected'])
        
        return processed
    
    def _determine_animal_type(self, label: str) -> str:
        """Определяет тип животного по лейблу"""
        label = label.lower()
        
        dog_keywords = ['dog', 'canine', 'puppy', 'retriever', 'shepherd', 'terrier', 'bulldog', 'labrador', 'beagle', 'poodle']
        cat_keywords = ['cat', 'feline', 'kitten', 'siamese', 'persian', 'tabby']
        bird_keywords = ['bird', 'parrot', 'canary', 'eagle', 'sparrow']
        
        if any(keyword in label for keyword in dog_keywords):
            return 'dog'
        elif any(keyword in label for keyword in cat_keywords):
            return 'cat'
        elif any(keyword in label for keyword in bird_keywords):
            return 'bird'
        else:
            return 'unknown'
    
    def _extract_breed_info(self, label: str) -> Optional[str]:
        """Извлекает информацию о породе из лейбла"""
        breed_indicators = [
            'retriever', 'shepherd', 'terrier', 'bulldog', 'labrador', 'beagle',
            'siamese', 'persian', 'maine', 'ragdoll', 'bengal'
        ]
        
        label_lower = label.lower()
        for breed in breed_indicators:
            if breed in label_lower:
                return breed.title()
        
        return None
    
    def _deduplicate_animals(self, animals: List[Dict]) -> List[Dict]:
        """Удаляет дубликаты животных"""
        seen_types = {}
        result = []
        
        # Сортируем по уверенности (убывание)
        animals.sort(key=lambda x: x['confidence'], reverse=True)
        
        for animal in animals:
            animal_type = animal['type']
            if animal_type not in seen_types:
                seen_types[animal_type] = True
                result.append(animal)
        
        return result


class LocalYOLOAnalyzer:
    """Локальный анализатор на основе YOLO"""
    
    def __init__(self, model_size: str = 'n'):
        """
        Инициализация YOLO модели
        model_size: 'n' (nano), 's' (small), 'm' (medium), 'l' (large), 'x' (extra-large)
        """
        self.model = None
        self.model_size = model_size
        self.animal_classes = {
            15: 'bird', 16: 'cat', 17: 'dog', 18: 'horse', 
            19: 'sheep', 20: 'cow', 21: 'elephant', 22: 'bear', 
            23: 'zebra', 24: 'giraffe'
        }
        
        # Отложенная загрузка модели
        self._initialize_model()
    
    def _initialize_model(self):
        """Инициализация YOLO модели"""
        try:
            from ultralytics import YOLO
            model_name = f'yolov8{self.model_size}.pt'
            
            logger.info(f"Loading YOLO model: {model_name}")
            self.model = YOLO(model_name)
            logger.info("YOLO model loaded successfully")
            
        except ImportError:
            logger.warning("ultralytics not installed. Install with: pip install ultralytics")
            self.model = None
        except Exception as e:
            logger.error(f"Error loading YOLO model: {e}")
            self.model = None
    
    def analyze_image(self, image: Image.Image) -> Dict[str, Any]:
        """Анализ изображения с помощью YOLO"""
        if self.model is None:
            logger.warning("YOLO model not available")
            return {'animals_detected': [], 'total_objects': 0, 'source': 'local_yolo_unavailable'}
        
        try:
            # Конвертируем PIL в numpy array
            img_array = np.array(image)
            
            # Запускаем inference
            results = self.model(img_array, verbose=False)
            
            animals_found = []
            total_detections = 0
            
            for result in results:
                boxes = result.boxes
                if boxes is not None:
                    total_detections = len(boxes)
                    
                    for box in boxes:
                        class_id = int(box.cls[0])
                        confidence = float(box.conf[0])
                        
                        if class_id in self.animal_classes and confidence > 0.5:
                            animals_found.append({
                                'type': self.animal_classes[class_id],
                                'confidence': confidence,
                                'bbox': box.xyxy[0].tolist(),
                                'class_id': class_id
                            })
            
            logger.info(f"YOLO analysis: {len(animals_found)} animals detected from {total_detections} total objects")
            
            return {
                'animals_detected': animals_found,
                'total_objects': total_detections,
                'source': 'local_yolo'
            }
            
        except Exception as e:
            logger.error(f"Error in YOLO analysis: {e}")
            return {'animals_detected': [], 'total_objects': 0, 'source': 'local_yolo_error'}


class FreeHybridAnalyzer:
    """Гибридный анализатор с бесплатными API"""
    
    def __init__(self, hf_api: Optional[HuggingFaceVisionAPI] = None, local_yolo: Optional[LocalYOLOAnalyzer] = None):
        self.hf_api = hf_api
        self.local_yolo = local_yolo
        
        # Статистика анализаторов
        self.available_analyzers = []
        if hf_api:
            self.available_analyzers.append('huggingface')
        if local_yolo and local_yolo.model:
            self.available_analyzers.append('local_yolo')
        
        logger.info(f"Free hybrid analyzer initialized with: {', '.join(self.available_analyzers)}")
    
    async def comprehensive_analysis(self, image_data: bytes) -> Dict[str, Any]:
        """Комплексный анализ с бесплатными решениями"""
        try:
            results = {
                'analysis_sources': self.available_analyzers,
                'hf_result': {},
                'local_result': {},
                'combined_result': {},
                'processing_time': 0
            }
            
            import time
            start_time = time.time()
            
            # Подготавливаем задачи для параллельного выполнения
            tasks = []
            
            # Hugging Face анализ (асинхронно)
            if self.hf_api:
                tasks.append(self._run_hf_analysis(image_data))
            else:
                tasks.append(self._mock_async_result({}))
            
            # Локальный YOLO анализ (синхронно, но в отдельной задаче)
            if self.local_yolo:
                tasks.append(self._run_local_analysis(image_data))
            else:
                tasks.append(self._mock_async_result({}))
            
            # Выполняем анализы параллельно
            hf_result, local_result = await asyncio.gather(*tasks, return_exceptions=True)
            
            # Обрабатываем исключения
            if isinstance(hf_result, Exception):
                logger.error(f"HuggingFace analysis failed: {hf_result}")
                hf_result = {}
            
            if isinstance(local_result, Exception):
                logger.error(f"Local analysis failed: {local_result}")
                local_result = {}
            
            results['hf_result'] = hf_result
            results['local_result'] = local_result
            results['processing_time'] = time.time() - start_time
            
            # Комбинируем результаты
            results['combined_result'] = self._combine_free_results(hf_result, local_result)
            
            logger.info(f"Free analysis completed in {results['processing_time']:.2f}s")
            return results
            
        except Exception as e:
            logger.error(f"Error in free comprehensive analysis: {e}")
            return {
                'analysis_sources': [],
                'error': str(e),
                'combined_result': {}
            }
    
    async def _run_hf_analysis(self, image_data: bytes) -> Dict:
        """Запуск HuggingFace анализа"""
        return await self.hf_api.analyze_image(image_data)
    
    async def _run_local_analysis(self, image_data: bytes) -> Dict:
        """Запуск локального анализа"""
        # Конвертируем bytes в PIL Image
        image = Image.open(io.BytesIO(image_data))
        return self.local_yolo.analyze_image(image)
    
    async def _mock_async_result(self, result: Dict) -> Dict:
        """Мок для недоступных анализаторов"""
        return result
    
    def _combine_free_results(self, hf_result: Dict, local_result: Dict) -> Dict[str, Any]:
        """Комбинирование бесплатных результатов"""
        combined = {
            'animal_type': 'unknown',
            'confidence': 0.0,
            'analysis_sources': self.available_analyzers,
            'hf_classifications': hf_result.get('classifications', []),
            'local_detections': local_result.get('animals_detected', []),
            'detailed_analysis': {
                'huggingface_animals': hf_result.get('animals_detected', []),
                'yolo_animals': local_result.get('animals_detected', []),
                'total_objects': local_result.get('total_objects', 0)
            },
            'source': 'unknown'
        }
        
        # Определяем лучший результат
        hf_animals = hf_result.get('animals_detected', [])
        local_animals = local_result.get('animals_detected', [])
        
        hf_confidence = max([a['confidence'] for a in hf_animals], default=0)
        local_confidence = max([a['confidence'] for a in local_animals], default=0)
        
        # Выбираем источник с лучшей уверенностью
        if hf_confidence > local_confidence and hf_animals:
            best_animal = max(hf_animals, key=lambda x: x['confidence'])
            combined['animal_type'] = best_animal['type']
            combined['confidence'] = best_animal['confidence']
            combined['source'] = 'huggingface'
            
            # Добавляем породную информацию если есть
            if 'breed_info' in best_animal and best_animal['breed_info']:
                combined['breed'] = best_animal['breed_info']
                
        elif local_animals:
            best_animal = max(local_animals, key=lambda x: x['confidence'])
            combined['animal_type'] = best_animal['type']
            combined['confidence'] = best_animal['confidence']
            combined['source'] = 'local_yolo'
        
        # Добавляем метаинформацию
        combined['meta'] = {
            'hf_available': bool(hf_result),
            'yolo_available': bool(local_result),
            'total_sources': len([r for r in [hf_result, local_result] if r])
        }
        
        return combined


def create_free_analyzer() -> Optional[FreeHybridAnalyzer]:
    """Создает бесплатный анализатор"""
    try:
        hf_api = None
        local_yolo = None
        
        # Инициализация HuggingFace API
        hf_key = os.getenv('HUGGINGFACE_API_KEY')
        if hf_key:
            try:
                hf_api = HuggingFaceVisionAPI(hf_key)
                logger.info("✅ HuggingFace API initialized")
            except Exception as e:
                logger.warning(f"Failed to initialize HuggingFace API: {e}")
        else:
            logger.info("ℹ️ HuggingFace API key not found, skipping HF integration")
        
        # Инициализация локального YOLO
        yolo_enabled = os.getenv('USE_LOCAL_YOLO', 'true').lower() == 'true'
        if yolo_enabled:
            try:
                model_size = os.getenv('YOLO_MODEL_SIZE', 'n')
                local_yolo = LocalYOLOAnalyzer(model_size)
                if local_yolo.model:
                    logger.info("✅ Local YOLO analyzer initialized")
                else:
                    logger.warning("❌ YOLO model not loaded")
                    local_yolo = None
            except Exception as e:
                logger.warning(f"Failed to initialize YOLO: {e}")
        else:
            logger.info("ℹ️ Local YOLO disabled in configuration")
        
        # Создаем гибридный анализатор
        if hf_api or local_yolo:
            analyzer = FreeHybridAnalyzer(hf_api, local_yolo)
            logger.info(f"🚀 Free hybrid analyzer created with {len(analyzer.available_analyzers)} sources")
            return analyzer
        else:
            logger.error("❌ No analyzers available")
            return None
        
    except Exception as e:
        logger.error(f"Error creating free analyzer: {e}")
        return None


# Функция быстрого тестирования
async def test_free_apis():
    """Быстрый тест бесплатных API"""
    logger.info("🧪 Testing free APIs...")
    
    analyzer = create_free_analyzer()
    if not analyzer:
        logger.error("No analyzer available for testing")
        return
    
    # Создаем тестовое изображение (белый квадрат)
    test_image = Image.new('RGB', (224, 224), color='white')
    img_byte_arr = io.BytesIO()
    test_image.save(img_byte_arr, format='JPEG')
    img_bytes = img_byte_arr.getvalue()
    
    # Тестируем анализ
    result = await analyzer.comprehensive_analysis(img_bytes)
    
    logger.info("Test completed:")
    logger.info(f"  Sources: {result.get('analysis_sources', [])}")
    logger.info(f"  Processing time: {result.get('processing_time', 0):.2f}s")
    logger.info(f"  Animal detected: {result['combined_result'].get('animal_type', 'none')}")
    logger.info(f"  Confidence: {result['combined_result'].get('confidence', 0):.2f}")


if __name__ == "__main__":
    # Настройка логирования для тестирования
    logging.basicConfig(level=logging.INFO)
    
    # Запуск теста
    asyncio.run(test_free_apis()) 