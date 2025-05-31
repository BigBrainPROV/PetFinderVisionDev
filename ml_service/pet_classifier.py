import torch
import torch.nn as nn
import torchvision.models as models
import torchvision.transforms as transforms
from PIL import Image
import numpy as np
import cv2
import logging
from typing import Dict, List, Tuple
from sklearn.metrics.pairwise import cosine_similarity
import json

class PetClassifier:
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        
        # Загружаем предобученную ResNet50
        self.model = models.resnet50(weights=models.ResNet50_Weights.IMAGENET1K_V2)
        
        # Удаляем последний слой для извлечения признаков
        self.feature_extractor = nn.Sequential(*list(self.model.children())[:-1])
        
        # Определяем преобразования для изображений
        self.transform = transforms.Compose([
            transforms.Resize(256),
            transforms.CenterCrop(224),
            transforms.ToTensor(),
            transforms.Normalize(
                mean=[0.485, 0.456, 0.406],
                std=[0.229, 0.224, 0.225]
            )
        ])
        
        # Устройство для вычислений
        self.device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
        self.model = self.model.to(self.device)
        self.feature_extractor = self.feature_extractor.to(self.device)
        
        # Переводим модели в режим оценки
        self.model.eval()
        self.feature_extractor.eval()
        
        # Загружаем классы ImageNet
        self.imagenet_classes = self._load_imagenet_classes()
        
        # Определяем породы для классификации
        self.dog_breeds = {
            151: 'german_shepherd',      # German shepherd
            154: 'siberian_husky',       # Siberian husky  
            207: 'golden_retriever',     # Golden retriever
            208: 'labrador_retriever',   # Labrador retriever
            156: 'rottweiler',           # Rottweiler
            160: 'french_bulldog',       # French bulldog
            245: 'beagle',               # Beagle
            242: 'boxer',                # Boxer
            265: 'poodle',               # Poodle
        }
        
        self.cat_breeds = {
            281: 'persian_cat',          # Persian cat
            282: 'siamese_cat',          # Siamese cat
            283: 'egyptian_mau',         # Egyptian cat
            284: 'bengal_cat',           # Tiger cat
            285: 'american_shorthair'    # Tabby cat
        }
        
        self.logger.info("PetClassifier инициализирован успешно")

    def _load_imagenet_classes(self):
        """Загрузка классов ImageNet"""
        try:
            with open('imagenet_classes.json', 'r') as f:
                return json.load(f)
        except:
            # Возвращаем базовый набор если файл не найден
            return ['unknown'] * 1000

    def extract_features(self, image: Image.Image) -> np.ndarray:
        """Извлечение глубоких признаков из изображения"""
        try:
            # Преобразуем изображение
            img_tensor = self.transform(image).unsqueeze(0).to(self.device)
            
            # Извлекаем признаки с помощью ResNet50
            with torch.no_grad():
                features = self.feature_extractor(img_tensor)
                features = features.squeeze().cpu().numpy()
            
            # Нормализуем признаки
            features = features / (np.linalg.norm(features) + 1e-8)
            
            return features
            
        except Exception as e:
            self.logger.error(f"Ошибка при извлечении признаков: {str(e)}")
            return np.zeros(2048)

    def classify_animal_type(self, image: Image.Image) -> Dict:
        """Определение типа животного (кошка/собака)"""
        try:
            img_tensor = self.transform(image).unsqueeze(0).to(self.device)
            
            with torch.no_grad():
                outputs = self.model(img_tensor)
                probabilities = torch.softmax(outputs, dim=1)[0]
            
            # Суммируем вероятности для собак и кошек
            dog_prob = sum(probabilities[idx] for idx in self.dog_breeds.keys())
            cat_prob = sum(probabilities[idx] for idx in self.cat_breeds.keys())
            
            if dog_prob > cat_prob and dog_prob > 0.1:
                return {'label': 'dog', 'confidence': float(dog_prob)}
            elif cat_prob > 0.1:
                return {'label': 'cat', 'confidence': float(cat_prob)}
            else:
                return {'label': 'unknown', 'confidence': 0.1}
                
        except Exception as e:
            self.logger.error(f"Ошибка классификации типа животного: {str(e)}")
            return {'label': 'unknown', 'confidence': 0.0}

    def classify_breed(self, image: Image.Image, animal_type: str) -> Dict:
        """Классификация породы на основе типа животного"""
        try:
            img_tensor = self.transform(image).unsqueeze(0).to(self.device)
            
            with torch.no_grad():
                outputs = self.model(img_tensor)
                probabilities = torch.softmax(outputs, dim=1)[0]
            
            if animal_type == 'dog':
                breed_probs = [(self.dog_breeds[idx], probabilities[idx]) for idx in self.dog_breeds.keys()]
            elif animal_type == 'cat':
                breed_probs = [(self.cat_breeds[idx], probabilities[idx]) for idx in self.cat_breeds.keys()]
            else:
                return {'label': 'unknown', 'confidence': 0.0}
            
            # Находим породу с максимальной вероятностью
            if breed_probs:
                best_breed, best_prob = max(breed_probs, key=lambda x: x[1])
                return {'label': best_breed, 'confidence': float(best_prob)}
            else:
                return {'label': 'unknown', 'confidence': 0.0}
                
        except Exception as e:
            self.logger.error(f"Ошибка классификации породы: {str(e)}")
            return {'label': 'unknown', 'confidence': 0.0}

    def analyze_color(self, image: Image.Image) -> Dict:
        """Анализ цвета и паттерна шерсти"""
        try:
            img_array = np.array(image.convert('RGB'))
            
            # Основные цвета в RGB
            color_ranges = {
                'black': ([0, 0, 0], [80, 80, 80]),
                'white': ([200, 200, 200], [255, 255, 255]),
                'brown': ([40, 20, 10], [120, 80, 60]),
                'orange': ([200, 100, 30], [255, 160, 80]),
                'gray': ([80, 80, 80], [160, 160, 160]),
                'golden': ([180, 140, 80], [255, 200, 120]),
                'cream': ([220, 200, 160], [255, 240, 200])
            }
            
            # Вычисляем средний цвет
            avg_color = np.mean(img_array, axis=(0, 1))
            
            # Находим ближайший цвет
            best_color = 'unknown'
            best_distance = float('inf')
            
            for color_name, (min_rgb, max_rgb) in color_ranges.items():
                center_rgb = [(min_rgb[i] + max_rgb[i]) / 2 for i in range(3)]
                distance = np.linalg.norm(avg_color - center_rgb)
                if distance < best_distance:
                    best_distance = distance
                    best_color = color_name
            
            # Определяем паттерн
            pattern = self._analyze_pattern(img_array)
            
            # Вычисляем уверенность на основе расстояния
            confidence = max(0.3, 1.0 - (best_distance / 255.0))
            
            return {
                'label': best_color,
                'confidence': confidence,
                'pattern': pattern
            }
            
        except Exception as e:
            self.logger.error(f"Ошибка анализа цвета: {str(e)}")
            return {'label': 'unknown', 'confidence': 0.0, 'pattern': 'solid'}

    def _analyze_pattern(self, img_array: np.ndarray) -> str:
        """Анализ паттерна окраса"""
        try:
            # Преобразуем в оттенки серого
            gray = cv2.cvtColor(img_array, cv2.COLOR_RGB2GRAY)
            
            # Вычисляем стандартное отклонение интенсивности
            std_intensity = np.std(gray)
            
            # Анализируем градиенты для обнаружения полос
            grad_x = cv2.Sobel(gray, cv2.CV_64F, 1, 0, ksize=3)
            grad_y = cv2.Sobel(gray, cv2.CV_64F, 0, 1, ksize=3)
            
            # Обнаружение полос
            lines_detected = np.std(grad_x) > 30 or np.std(grad_y) > 30
            
            if std_intensity > 50 and lines_detected:
                return 'striped'
            elif std_intensity > 40:
                return 'spotted'
            elif std_intensity < 20:
                return 'solid'
            else:
                return 'mixed'
                
        except:
            return 'solid'

    def detect_special_features(self, image: Image.Image) -> List[Dict]:
        """Обнаружение особых признаков (гетерохромия, шрамы, etc.)"""
        features = []
        
        try:
            img_array = np.array(image.convert('RGB'))
            
            # Простой алгоритм обнаружения гетерохромии
            # (в реальной системе здесь был бы более сложный алгоритм)
            if self._detect_heterochromia(img_array):
                features.append({'label': 'heterochromia', 'confidence': 0.8})
            
            # Обнаружение пушистости по текстуре
            if self._detect_fluffiness(img_array):
                features.append({'label': 'fluffy_coat', 'confidence': 0.7})
            
            return features
            
        except Exception as e:
            self.logger.error(f"Ошибка обнаружения особых признаков: {str(e)}")
            return []

    def _detect_heterochromia(self, img_array: np.ndarray) -> bool:
        """Простое обнаружение гетерохромии"""
        # Это упрощенная версия - в реальности нужен более сложный алгоритм
        # анализирующий области глаз
        return False

    def _detect_fluffiness(self, img_array: np.ndarray) -> bool:
        """Обнаружение пушистости по текстуре"""
        try:
            gray = cv2.cvtColor(img_array, cv2.COLOR_RGB2GRAY)
            
            # Используем детектор углов для анализа текстуры
            corners = cv2.goodFeaturesToTrack(gray, maxCorners=100, qualityLevel=0.01, minDistance=10)
            
            # Пушистая шерсть дает больше текстурных деталей
            return len(corners) > 50 if corners is not None else False
            
        except:
            return False

    def predict(self, image: Image.Image) -> Dict:
        """Полный анализ изображения питомца"""
        try:
            # Классифицируем тип животного
            animal_type = self.classify_animal_type(image)
            
            # Классифицируем породу
            breed = self.classify_breed(image, animal_type['label'])
            
            # Анализируем цвет и паттерн
            color_analysis = self.analyze_color(image)
            
            # Обнаруживаем особые признаки
            special_features = self.detect_special_features(image)
            
            return {
                'animal_type': animal_type,
                'breed': breed,
                'color': color_analysis,
                'special_features': special_features,
                'confidence': min(animal_type['confidence'], breed['confidence'])
            }
            
        except Exception as e:
            self.logger.error(f"Ошибка при анализе изображения: {str(e)}")
            return {
                'animal_type': {'label': 'unknown', 'confidence': 0.0},
                'breed': {'label': 'unknown', 'confidence': 0.0},
                'color': {'label': 'unknown', 'confidence': 0.0, 'pattern': 'solid'},
                'special_features': [],
                'confidence': 0.0
            }

    def find_similar_pets(self, query_features: np.ndarray, database_features: List[np.ndarray], top_k: int = 10) -> List[Tuple[int, float]]:
        """Поиск похожих питомцев по векторам признаков"""
        try:
            if len(database_features) == 0:
                return []
            
            # Преобразуем в numpy массивы
            query_features = query_features.reshape(1, -1)
            db_features = np.array(database_features)
            
            # Вычисляем косинусное сходство
            similarities = cosine_similarity(query_features, db_features)[0]
            
            # Получаем индексы отсортированные по убыванию сходства
            sorted_indices = np.argsort(similarities)[::-1]
            
            # Возвращаем топ-k результатов
            results = []
            for idx in sorted_indices[:top_k]:
                if similarities[idx] > 0.1:  # Минимальный порог сходства
                    results.append((int(idx), float(similarities[idx])))
            
            return results
            
        except Exception as e:
            self.logger.error(f"Ошибка поиска похожих питомцев: {str(e)}")
            return [] 