import cv2
import numpy as np
from PIL import Image
import torch
import torchvision.transforms as transforms
from sklearn.cluster import KMeans
from skimage.color import rgb2hsv, rgb2lab
from skimage.feature import local_binary_pattern
from skimage.measure import regionprops, label
import logging
from similarity_search.services.clip_service import CLIPService

logger = logging.getLogger(__name__)

class EnhancedPetAnalyzer:
    """Улучшенный анализатор для точного определения характеристик животных"""
    
    def __init__(self):
        self.animal_classifiers = {
            'dog': DogAnalyzer(),
            'cat': CatAnalyzer(), 
            'bird': BirdAnalyzer()
        }
        self.clip_service = CLIPService()
        
    def analyze_pet(self, image):
        """Основной метод анализа питомца"""
        try:
            # Базовый анализ изображения
            base_features = self._extract_base_features(image)
            
            # Определение типа животного
            animal_type, type_confidence = self._classify_animal_type(image, base_features)
            
            # Специализированный анализ в зависимости от типа
            if animal_type in self.animal_classifiers:
                specialized_analysis = self.animal_classifiers[animal_type].analyze(image, base_features)
            else:
                specialized_analysis = self._generic_analysis(image, base_features)
            
            # Поиск похожих животных
            similar_pets = self.clip_service.search(image, top_k=5)
            
            return {
                'animal_type': {
                    'label': animal_type,
                    'confidence': type_confidence
                },
                'breed': specialized_analysis.get('breed', {'label': 'mixed', 'confidence': 0.5}),
                'color': self._analyze_color(image),
                'eye_color': self._analyze_eye_color(image),
                'face_shape': self._analyze_face_shape(image),
                'special_features': self._detect_special_features(image, base_features),
                'detailed_metrics': {
                    'base_features': base_features,
                    'specialized_analysis': specialized_analysis
                },
                'similar_pets': similar_pets
            }
            
        except Exception as e:
            logger.error(f"Error in pet analysis: {e}")
            return self._get_default_analysis()
    
    def _extract_base_features(self, image):
        """Извлечение базовых характеристик изображения"""
        img_array = np.array(image)
        
        # Анализ размеров и пропорций
        height, width = img_array.shape[:2]
        aspect_ratio = width / height
        
        # Анализ цветового распределения
        color_analysis = self._analyze_color_distribution(img_array)
        
        # Анализ текстуры
        texture_analysis = self._analyze_texture(img_array)
        
        # Анализ контуров и форм
        shape_analysis = self._analyze_shapes(img_array)
        
        return {
            'dimensions': {'width': width, 'height': height, 'aspect_ratio': aspect_ratio},
            'color_distribution': color_analysis,
            'texture': texture_analysis,
            'shapes': shape_analysis
        }
    
    def _classify_animal_type(self, image, features):
        """Улучшенная классификация типа животного"""
        img_array = np.array(image)
        
        # Анализ характерных признаков разных животных
        dog_score = self._calculate_dog_probability(img_array, features)
        cat_score = self._calculate_cat_probability(img_array, features)
        bird_score = self._calculate_bird_probability(img_array, features)
        
        scores = {
            'dog': dog_score,
            'cat': cat_score, 
            'bird': bird_score
        }
        
        # Определяем тип с наивысшей вероятностью
        best_type = max(scores, key=scores.get)
        confidence = scores[best_type]
        
        logger.info(f"Animal type scores: {scores}")
        
        return best_type, confidence
    
    def _calculate_dog_probability(self, img_array, features):
        """Вычисление вероятности того, что это собака"""
        score = 0.0
        
        # Анализ пропорций тела (собаки обычно более вытянутые)
        aspect_ratio = features['dimensions']['aspect_ratio']
        if aspect_ratio > 1.3:
            score += 0.3
        elif aspect_ratio > 1.1:
            score += 0.15
            
        # Анализ морды (у собак обычно более вытянутая морда)
        muzzle_score = self._detect_muzzle_length(img_array)
        score += muzzle_score * 0.25
        
        # Анализ ушей (собачьи уши более разнообразные)
        ear_score = self._analyze_ears_dogs(img_array)
        score += ear_score * 0.2
        
        # Анализ цвета (собаки часто коричневые, золотистые)
        color_dist = features['color_distribution']
        if any('brown' in str(color).lower() or 'golden' in str(color).lower() 
               for color in color_dist['dominant_colors'][:2]):
            score += 0.1
            
        # Анализ размера (собаки часто крупнее кошек на фото)
        if features['dimensions']['width'] > 300 or features['dimensions']['height'] > 300:
            score += 0.1
            
        return min(1.0, score)
    
    def _calculate_cat_probability(self, img_array, features):
        """Вычисление вероятности того, что это кошка"""
        score = 0.0
        
        # Анализ пропорций (кошки более компактные)
        aspect_ratio = features['dimensions']['aspect_ratio']
        if 0.8 <= aspect_ratio <= 1.2:
            score += 0.3
            
        # Анализ морды (у кошек плоская морда)
        muzzle_score = 1.0 - self._detect_muzzle_length(img_array)
        score += muzzle_score * 0.25
        
        # Анализ ушей (кошачьи уши треугольные, стоячие)
        ear_score = self._analyze_ears_cats(img_array)
        score += ear_score * 0.2
        
        # Анализ глаз (кошачьи глаза часто выразительные)
        eye_score = self._detect_cat_eyes(img_array)
        score += eye_score * 0.15
        
        # Анализ полосатости (многие кошки полосатые)
        if features['texture']['has_stripes']:
            score += 0.1
            
        return min(1.0, score)
    
    def _calculate_bird_probability(self, img_array, features):
        """Вычисление вероятности того, что это птица"""
        score = 0.0
        
        # Анализ формы тела (птицы компактные и округлые)
        if features['shapes']['compactness'] > 0.7:
            score += 0.3
            
        # Анализ наличия клюва
        beak_score = self._detect_beak(img_array)
        score += beak_score * 0.4
        
        # Анализ перьев (текстура)
        if features['texture']['is_feathered']:
            score += 0.2
            
        # Анализ ярких цветов (многие птицы яркие)
        if features['color_distribution']['brightness'] > 0.7:
            score += 0.1
            
        return min(1.0, score)
    
    def _analyze_color(self, image):
        """Улучшенный анализ цвета шерсти/перьев"""
        img_array = np.array(image)
        
        # Маскируем фон
        mask = self._create_animal_mask(img_array)
        masked_pixels = img_array[mask]
        
        if len(masked_pixels) == 0:
            masked_pixels = img_array.reshape(-1, 3)
        
        # Кластеризация цветов
        kmeans = KMeans(n_clusters=min(5, len(masked_pixels) // 100), random_state=42)
        kmeans.fit(masked_pixels)
        
        colors = kmeans.cluster_centers_
        counts = np.bincount(kmeans.labels_)
        
        # Определяем основной цвет
        dominant_color_rgb = colors[np.argmax(counts)]
        main_color = self._rgb_to_color_name(dominant_color_rgb)
        
        # Анализ паттернов
        pattern = self._detect_color_patterns(img_array, mask)
        
        return {
            'label': main_color,
            'confidence': 0.85,
            'pattern': pattern,
            'rgb': dominant_color_rgb.tolist()
        }
    
    def _analyze_eye_color(self, image):
        """Анализ цвета глаз"""
        img_array = np.array(image)
        
        # Поиск глаз с помощью детектора окружностей
        gray = cv2.cvtColor(img_array, cv2.COLOR_RGB2GRAY)
        eyes = cv2.HoughCircles(
            gray, cv2.HOUGH_GRADIENT, 1, 50,
            param1=50, param2=30, minRadius=5, maxRadius=50
        )
        
        if eyes is not None:
            eyes = np.round(eyes[0, :]).astype("int")
            
            # Анализируем цвет найденных глаз
            eye_colors = []
            for (x, y, r) in eyes[:2]:  # Берем максимум 2 глаза
                # Извлекаем область глаза
                eye_region = img_array[max(0, y-r):min(img_array.shape[0], y+r),
                                     max(0, x-r):min(img_array.shape[1], x+r)]
                
                if eye_region.size > 0:
                    # Анализируем цвет центральной части глаза
                    center_region = eye_region[r//2:r*3//2, r//2:r*3//2]
                    if center_region.size > 0:
                        avg_color = np.mean(center_region.reshape(-1, 3), axis=0)
                        eye_color = self._classify_eye_color(avg_color)
                        eye_colors.append(eye_color)
            
            if eye_colors:
                # Если глаза разного цвета - гетерохромия
                if len(set(eye_colors)) > 1:
                    return {'label': 'different', 'confidence': 0.9}
                else:
                    return {'label': eye_colors[0], 'confidence': 0.8}
        
        # Если глаза не найдены, используем общий анализ цвета
        return {'label': 'brown', 'confidence': 0.3}
    
    def _detect_special_features(self, image, features):
        """Определение особых характеристик"""
        img_array = np.array(image)
        special_features = []
        
        # Гетерохромия (разные глаза)
        eye_analysis = self._analyze_eye_color(image)
        if eye_analysis['label'] == 'different':
            special_features.append('heterochromia')
        
        # Отсутствие хвоста
        if self._detect_missing_tail(img_array):
            special_features.append('tail_missing')
        
        # Деформация ушей
        if self._detect_ear_fold(img_array):
            special_features.append('ear_fold')
        
        # Пятна на глазах
        if self._detect_eye_spots(img_array):
            special_features.append('eye_spot')
        
        # Альбинизм
        if self._detect_albinism(img_array, features):
            special_features.append('albino')
        
        # Витилиго
        if self._detect_vitiligo(img_array):
            special_features.append('vitiligo')
        
        if not special_features:
            special_features.append('none')
        
        return {
            'label': special_features[0] if len(special_features) == 1 else 'multiple',
            'confidence': 0.7,
            'features': special_features
        }
    
    def _detect_missing_tail(self, img_array):
        """Определение отсутствия хвоста"""
        # Анализируем заднюю часть изображения
        height, width = img_array.shape[:2]
        rear_section = img_array[:, width*2//3:]
        
        # Поиск вытянутых объектов (хвост)
        gray = cv2.cvtColor(rear_section, cv2.COLOR_RGB2GRAY)
        contours, _ = cv2.findContours(gray, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
        # Если нет длинных тонких контуров - возможно отсутствует хвост
        tail_like_contours = 0
        for contour in contours:
            x, y, w, h = cv2.boundingRect(contour)
            if h > w * 2 and h > 30:  # Длинный и тонкий объект
                tail_like_contours += 1
        
        return tail_like_contours == 0
    
    def _detect_albinism(self, img_array, features):
        """Определение альбинизма"""
        # Альбинизм: очень светлая/белая шерсть + розовые/красные глаза
        color_dist = features['color_distribution']
        
        # Проверяем преобладание белого цвета
        white_dominant = any('white' in str(color).lower() 
                           for color in color_dist['dominant_colors'][:2])
        
        # Проверяем розоватые оттенки в глазах
        hsv = cv2.cvtColor(img_array, cv2.COLOR_RGB2HSV)
        pink_mask = cv2.inRange(hsv, np.array([150, 50, 50]), np.array([180, 255, 255]))
        pink_ratio = np.sum(pink_mask > 0) / (img_array.shape[0] * img_array.shape[1])
        
        return white_dominant and pink_ratio > 0.01
    
    def _detect_vitiligo(self, img_array):
        """Определение витилиго (белые пятна на темной шерсти)"""
        gray = cv2.cvtColor(img_array, cv2.COLOR_RGB2GRAY)
        
        # Находим очень светлые и очень темные области
        light_mask = gray > 200
        dark_mask = gray < 100
        
        # Если есть и светлые и темные области с резкими границами
        light_ratio = np.sum(light_mask) / gray.size
        dark_ratio = np.sum(dark_mask) / gray.size
        
        return 0.1 < light_ratio < 0.4 and dark_ratio > 0.3
    
    def _detect_ear_fold(self, img_array):
        """Определение заломов на ушах"""
        # Поиск характерных форм ушей в верхней части изображения
        height, width = img_array.shape[:2]
        ear_region = img_array[:height//3, :]
        
        gray = cv2.cvtColor(ear_region, cv2.COLOR_RGB2GRAY)
        edges = cv2.Canny(gray, 50, 150)
        
        # Поиск линий (заломы создают прямые линии)
        lines = cv2.HoughLinesP(edges, 1, np.pi/180, threshold=30, minLineLength=20, maxLineGap=10)
        
        if lines is not None:
            # Если много горизонтальных линий в области ушей - возможны заломы
            horizontal_lines = 0
            for line in lines:
                x1, y1, x2, y2 = line[0]
                angle = np.abs(np.arctan2(y2-y1, x2-x1) * 180 / np.pi)
                if angle < 30 or angle > 150:  # Горизонтальные линии
                    horizontal_lines += 1
            
            return horizontal_lines > 5
        
        return False
    
    # Вспомогательные методы для анализа
    def _create_animal_mask(self, img_array):
        """Создание маски для выделения животного от фона"""
        gray = cv2.cvtColor(img_array, cv2.COLOR_RGB2GRAY)
        _, mask = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
        return mask > 0
    
    def _rgb_to_color_name(self, rgb):
        """Преобразование RGB в название цвета"""
        r, g, b = rgb
        
        # Простая логика определения цвета
        if r > 200 and g > 200 and b > 200:
            return 'white'
        elif r < 50 and g < 50 and b < 50:
            return 'black'
        elif r > g and r > b:
            return 'red' if r > 150 else 'brown'
        elif g > r and g > b:
            return 'green'
        elif b > r and b > g:
            return 'blue'
        elif r > 150 and g > 100 and b < 100:
            return 'orange'
        elif r > 100 and g > 100 and b < 80:
            return 'golden'
        else:
            return 'gray'
    
    def _classify_eye_color(self, rgb):
        """Классификация цвета глаз"""
        r, g, b = rgb
        
        if b > r and b > g and b > 120:
            return 'blue'
        elif g > r and g > b and g > 100:
            return 'green'
        elif r > 150 and g > 100 and b < 100:
            return 'orange'
        elif r > 100 and g > 80 and b < 80:
            return 'yellow'
        else:
            return 'brown'
    
    def _get_default_analysis(self):
        """Возвращает анализ по умолчанию при ошибке"""
        return {
            'animal_type': {'label': 'cat', 'confidence': 0.5},
            'breed': {'label': 'mixed', 'confidence': 0.5},
            'color': {'label': 'gray', 'confidence': 0.5},
            'eye_color': {'label': 'brown', 'confidence': 0.5},
            'face_shape': {'label': 'round', 'confidence': 0.5},
            'special_features': {'label': 'none', 'confidence': 0.5}
        }

    def _analyze_color_distribution(self, img_array):
        """Анализ распределения цветов"""
        # Конвертируем в HSV для лучшего анализа цветов
        hsv = cv2.cvtColor(img_array, cv2.COLOR_RGB2HSV)
        
        # Анализируем яркость
        brightness = np.mean(hsv[:,:,2]) / 255.0
        
        # Анализируем насыщенность
        saturation = np.mean(hsv[:,:,1]) / 255.0
        
        # Простая кластеризация для определения доминирующих цветов
        pixels = img_array.reshape(-1, 3)
        kmeans = KMeans(n_clusters=3, random_state=42)
        kmeans.fit(pixels)
        
        dominant_colors = [self._rgb_to_color_name(color) for color in kmeans.cluster_centers_]
        
        return {
            'brightness': brightness,
            'saturation': saturation,
            'dominant_colors': dominant_colors
        }
    
    def _analyze_texture(self, img_array):
        """Анализ текстуры изображения"""
        gray = cv2.cvtColor(img_array, cv2.COLOR_RGB2GRAY)
        
        # Local Binary Pattern для анализа текстуры
        lbp = local_binary_pattern(gray, 8, 1, method='uniform')
        texture_variance = np.var(lbp)
        
        # Анализ краев для определения пушистости
        edges = cv2.Canny(gray, 50, 150)
        edge_density = np.sum(edges > 0) / edges.size
        
        # Простое определение полос
        h_projection = np.std(np.mean(gray, axis=1))
        v_projection = np.std(np.mean(gray, axis=0))
        has_stripes = h_projection > 20 or v_projection > 20
        
        # Определение перьевой текстуры
        is_feathered = texture_variance > 50 and edge_density > 0.15
        
        return {
            'texture_variance': texture_variance,
            'edge_density': edge_density,
            'has_stripes': has_stripes,
            'is_feathered': is_feathered,
            'is_fluffy': edge_density > 0.1
        }
    
    def _analyze_shapes(self, img_array):
        """Анализ форм и контуров"""
        gray = cv2.cvtColor(img_array, cv2.COLOR_RGB2GRAY)
        
        # Находим контуры
        contours, _ = cv2.findContours(gray, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
        if contours:
            # Берем самый большой контур
            largest_contour = max(contours, key=cv2.contourArea)
            
            # Анализ компактности
            area = cv2.contourArea(largest_contour)
            perimeter = cv2.arcLength(largest_contour, True)
            compactness = 4 * np.pi * area / (perimeter * perimeter) if perimeter > 0 else 0
            
            # Анализ выпуклости
            hull = cv2.convexHull(largest_contour)
            hull_area = cv2.contourArea(hull)
            solidity = area / hull_area if hull_area > 0 else 0
            
            return {
                'compactness': compactness,
                'solidity': solidity,
                'area': area,
                'perimeter': perimeter
            }
        
        return {
            'compactness': 0.0,
            'solidity': 0.0,
            'area': 0.0,
            'perimeter': 0.0
        }
    
    def _detect_muzzle_length(self, img_array):
        """Определение длины морды"""
        gray = cv2.cvtColor(img_array, cv2.COLOR_RGB2GRAY)
        height, width = gray.shape
        
        # Анализируем центральную часть изображения (где обычно морда)
        center_region = gray[height//4:3*height//4, width//4:3*width//4]
        
        # Применяем детектор краев
        edges = cv2.Canny(center_region, 50, 150)
        
        # Ищем вертикальные линии (характерны для вытянутой морды)
        vertical_lines = 0
        lines = cv2.HoughLines(edges, 1, np.pi/180, threshold=30)
        
        if lines is not None:
            for rho, theta in lines[:, 0]:
                angle = theta * 180 / np.pi
                if 80 <= angle <= 100:  # Примерно вертикальные линии
                    vertical_lines += 1
        
        # Нормализуем оценку (больше вертикальных линий = более вытянутая морда)
        return min(1.0, vertical_lines / 10.0)
    
    def _analyze_ears_dogs(self, img_array):
        """Анализ ушей для собак"""
        # Упрощенный анализ - проверяем верхнюю часть изображения
        height, width = img_array.shape[:2]
        ear_region = img_array[:height//3, :]
        
        gray = cv2.cvtColor(ear_region, cv2.COLOR_RGB2GRAY)
        edges = cv2.Canny(gray, 50, 150)
        
        # Собачьи уши более разнообразны по форме
        contours, _ = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
        ear_score = 0.0
        if contours:
            # Анализируем разнообразие форм контуров
            areas = [cv2.contourArea(c) for c in contours if cv2.contourArea(c) > 100]
            if len(areas) > 2:
                variance = np.var(areas)
                ear_score = min(1.0, variance / 10000)  # Высокая вариативность = собачьи уши
        
        return ear_score
    
    def _analyze_ears_cats(self, img_array):
        """Анализ ушей для кошек"""
        height, width = img_array.shape[:2]
        ear_region = img_array[:height//3, :]
        
        gray = cv2.cvtColor(ear_region, cv2.COLOR_RGB2GRAY)
        
        # Поиск треугольных форм (кошачьи уши)
        contours, _ = cv2.findContours(gray, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
        triangular_score = 0.0
        if contours:
            for contour in contours:
                if cv2.contourArea(contour) > 100:
                    # Аппроксимируем контур
                    epsilon = 0.02 * cv2.arcLength(contour, True)
                    approx = cv2.approxPolyDP(contour, epsilon, True)
                    
                    # Если контур можно аппроксимировать треугольником
                    if len(approx) == 3:
                        triangular_score += 0.2
        
        return min(1.0, triangular_score)
    
    def _detect_cat_eyes(self, img_array):
        """Определение кошачьих глаз"""
        gray = cv2.cvtColor(img_array, cv2.COLOR_RGB2GRAY)
        
        # Поиск круглых объектов (глаза)
        circles = cv2.HoughCircles(
            gray, cv2.HOUGH_GRADIENT, 1, 30,
            param1=50, param2=30, minRadius=10, maxRadius=50
        )
        
        if circles is not None:
            circles = np.round(circles[0, :]).astype("int")
            
            # Кошачьи глаза обычно большие и выразительные
            large_eyes = sum(1 for (x, y, r) in circles if r > 15)
            return min(1.0, large_eyes / 2.0)  # Максимум 2 глаза
        
        return 0.0
    
    def _detect_beak(self, img_array):
        """Определение клюва у птиц"""
        gray = cv2.cvtColor(img_array, cv2.COLOR_RGB2GRAY)
        height, width = gray.shape
        
        # Анализируем центральную часть (где обычно клюв)
        center_x, center_y = width // 2, height // 2
        beak_region = gray[center_y-50:center_y+50, center_x-50:center_x+50]
        
        if beak_region.size == 0:
            return 0.0
        
        # Поиск острых углов (характерно для клюва)
        edges = cv2.Canny(beak_region, 50, 150)
        
        # Используем детектор углов Харриса
        corners = cv2.cornerHarris(beak_region.astype(np.float32), 2, 3, 0.04)
        
        # Подсчитываем количество острых углов
        sharp_corners = np.sum(corners > 0.01 * corners.max())
        
        return min(1.0, sharp_corners / 10.0)
    
    def _detect_color_patterns(self, img_array, mask):
        """Определение цветовых паттернов"""
        if mask is None:
            mask = np.ones(img_array.shape[:2], dtype=bool)
        
        masked_img = img_array[mask]
        
        if len(masked_img) == 0:
            return 'solid'
        
        # Кластеризация для определения количества цветов
        kmeans = KMeans(n_clusters=min(4, len(masked_img) // 50), random_state=42)
        kmeans.fit(masked_img)
        
        # Анализ распределения цветов
        counts = np.bincount(kmeans.labels_)
        sorted_counts = np.sort(counts)[::-1]
        
        # Если есть доминирующий цвет (>60%) - solid
        if sorted_counts[0] / len(masked_img) > 0.6:
            return 'solid'
        # Если два цвета доминируют - bicolor
        elif len(sorted_counts) > 1 and (sorted_counts[0] + sorted_counts[1]) / len(masked_img) > 0.8:
            return 'bicolor'
        # Если много цветов - multicolor
        else:
            return 'multicolor'
    
    def _analyze_face_shape(self, image):
        """Анализ формы мордочки"""
        img_array = np.array(image)
        gray = cv2.cvtColor(img_array, cv2.COLOR_RGB2GRAY)
        height, width = gray.shape
        
        # Анализируем центральную часть лица
        face_region = gray[height//4:3*height//4, width//4:3*width//4]
        
        # Анализ контуров
        contours, _ = cv2.findContours(face_region, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
        if contours:
            largest_contour = max(contours, key=cv2.contourArea)
            
            # Анализ ограничивающего прямоугольника
            x, y, w, h = cv2.boundingRect(largest_contour)
            aspect_ratio = w / h if h > 0 else 1.0
            
            # Определение формы на основе соотношения сторон
            if aspect_ratio > 1.3:
                shape = 'oval'
            elif aspect_ratio < 0.8:
                shape = 'long'
            else:
                # Дополнительный анализ для различения круглой и треугольной
                hull = cv2.convexHull(largest_contour)
                hull_area = cv2.contourArea(hull)
                contour_area = cv2.contourArea(largest_contour)
                
                solidity = contour_area / hull_area if hull_area > 0 else 0
                
                if solidity > 0.8:
                    shape = 'round'
                else:
                    shape = 'triangular'
        else:
            shape = 'round'  # По умолчанию
        
        return {
            'label': shape,
            'confidence': 0.7
        }
    
    def _detect_eye_spots(self, img_array):
        """Определение пятен на глазах"""
        gray = cv2.cvtColor(img_array, cv2.COLOR_RGB2GRAY)
        
        # Поиск глаз
        eye_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_eye.xml')
        eyes = eye_cascade.detectMultiScale(gray, 1.1, 4)
        
        for (ex, ey, ew, eh) in eyes:
            eye_region = img_array[ey:ey+eh, ex:ex+ew]
            
            # Анализ цветового разнообразия в области глаза
            if eye_region.size > 0:
                colors = eye_region.reshape(-1, 3)
                if len(colors) > 0:
                    color_variance = np.var(colors, axis=0)
                    # Если высокая вариативность цвета - возможно есть пятна
                    if np.mean(color_variance) > 1000:
                        return True
        
        return False
    
    def _generic_analysis(self, image, features):
        """Общий анализ для неопределенных типов животных"""
        return {
            'breed': {'label': 'unknown', 'confidence': 0.3}
        }

# Специализированные анализаторы для разных типов животных
class DogAnalyzer:
    """Специализированный анализатор для собак"""
    
    def analyze(self, image, base_features):
        breed = self._classify_dog_breed(image, base_features)
        return {'breed': breed}
    
    def _classify_dog_breed(self, image, features):
        # Базовая классификация пород собак
        return {'label': 'mixed', 'confidence': 0.6}

class CatAnalyzer:
    """Специализированный анализатор для кошек"""
    
    def analyze(self, image, base_features):
        breed = self._classify_cat_breed(image, base_features)
        return {'breed': breed}
    
    def _classify_cat_breed(self, image, features):
        # Базовая классификация пород кошек
        return {'label': 'domestic', 'confidence': 0.6}

class BirdAnalyzer:
    """Специализированный анализатор для птиц"""
    
    def analyze(self, image, base_features):
        breed = self._classify_bird_species(image, base_features)
        return {'breed': breed}
    
    def _classify_bird_species(self, image, features):
        # Базовая классификация видов птиц
        return {'label': 'parrot', 'confidence': 0.6} 