import json
import io
from typing import List, Optional, Dict, Tuple
import psycopg2
import psycopg2.extras
from datetime import datetime, timedelta
import uuid

from fastapi import FastAPI, UploadFile, File, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
import logging
import sys

from models import ImageAnalysis, SearchResponse, AnimalType, Breed, Feature, LostPetAd, Location, Contact

# Настройка логирования
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    stream=sys.stdout
)
logger = logging.getLogger(__name__)

app = FastAPI()

# Настройка CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Словари пород для распознавания по имени файла
DOG_BREEDS = {
    # Популярные породы собак
    'husky': 'хаски',
    'хаски': 'хаски',
    'golden_retriever': 'золотистый ретривер',
    'ретривер': 'золотистый ретривер',
    'german_shepherd': 'немецкая овчарка',
    'овчарка': 'немецкая овчарка',
    'shepherd': 'овчарка',
    'labrador': 'лабрадор',
    'лабрадор': 'лабрадор',
    'bulldog': 'бульдог',
    'бульдог': 'бульдог',
    'poodle': 'пудель',
    'пудель': 'пудель',
    'chihuahua': 'чихуахуа',
    'чихуахуа': 'чихуахуа',
    'rottweiler': 'ротвейлер',
    'ротвейлер': 'ротвейлер',
    'beagle': 'бигль',
    'бигль': 'бигль',
    'boxer': 'боксер',
    'боксер': 'боксер',
    'yorkshire': 'йоркширский терьер',
    'йорк': 'йоркширский терьер',
    'yorkie': 'йоркширский терьер',
    'dachshund': 'такса',
    'такса': 'такса',
    'pomeranian': 'шпиц',
    'шпиц': 'шпиц',
    'border_collie': 'бордер-колли',
    'колли': 'бордер-колли',
    'corgi': 'корги',
    'корги': 'корги',
    'maltese': 'мальтезе',
    'мальтезе': 'мальтезе',
    'jack_russell': 'джек-рассел терьер',
    'терьер': 'терьер',
    'shih_tzu': 'ши-тцу',
    'ши_тцу': 'ши-тцу',
    'pitbull': 'питбуль',
    'питбуль': 'питбуль',
    'mastiff': 'мастиф',
    'мастиф': 'мастиф',
    'doberman': 'доберман',
    'доберман': 'доберман',
    'аляскинский_маламут': 'аляскинский маламут',
    'malamute': 'аляскинский маламут',
    'akita': 'акита',
    'акита': 'акита',
    'кокер_спаниель': 'кокер-спаниель',
    'spaniel': 'спаниель'
}

CAT_BREEDS = {
    # Популярные породы кошек
    'persian': 'персидская',
    'персидская': 'персидская',
    'siamese': 'сиамская',
    'сиамская': 'сиамская',
    'maine_coon': 'мейн-кун',
    'мейн_кун': 'мейн-кун',
    'british': 'британская',
    'британская': 'британская',
    'scottish': 'шотландская',
    'шотландская': 'шотландская',
    'sphynx': 'сфинкс',
    'сфинкс': 'сфинкс',
    'bengal': 'бенгальская',
    'бенгальская': 'бенгальская',
    'ragdoll': 'рэгдолл',
    'рэгдолл': 'рэгдолл',
    'abyssinian': 'абиссинская',
    'абиссинская': 'абиссинская',
    'russian_blue': 'русская голубая',
    'русская_голубая': 'русская голубая',
    'russian': 'русская',
    'norwegian': 'норвежская лесная',
    'норвежская': 'норвежская лесная',
    'birman': 'бирманская',
    'бирманская': 'бирманская',
    'burmese': 'бурманская',
    'бурманская': 'бурманская',
    'oriental': 'ориентальная',
    'ориентальная': 'ориентальная',
    'turkish': 'турецкая',
    'турецкая': 'турецкая',
    'exotic': 'экзот',
    'экзот': 'экзот',
    'manx': 'мэнкс',
    'мэнкс': 'мэнкс',
    'devon_rex': 'девон-рекс',
    'девон_рекс': 'девон-рекс',
    'cornish_rex': 'корниш-рекс',
    'корниш_рекс': 'корниш-рекс',
    'ragamuffin': 'рагамаффин',
    'рагамаффин': 'рагамаффин',
    'домашняя': 'домашняя',
    'беспородная': 'беспородная'
}

# Породы птиц
BIRD_BREEDS = {
    'pigeon': 'голубь',
    'голубь': 'голубь',
    'dove': 'голубь',
    'parrot': 'попугай',
    'попугай': 'попугай',
    'canary': 'канарейка',
    'канарейка': 'канарейка',
    'budgie': 'волнистый попугайчик',
    'волнистый': 'волнистый попугайчик',
    'cockatiel': 'корелла',
    'корелла': 'корелла',
    'lovebird': 'неразлучник',
    'неразлучник': 'неразлучник',
    'finch': 'зяблик',
    'зяблик': 'зяблик',
    'robin': 'малиновка',
    'малиновка': 'малиновка',
    'sparrow': 'воробей',
    'воробей': 'воробей',
    'crow': 'ворона',
    'ворона': 'ворона',
    'eagle': 'орел',
    'орел': 'орел',
    'hawk': 'ястреб',
    'ястреб': 'ястреб'
}

# Породы кроликов
RABBIT_BREEDS = {
    'domestic': 'домашний',
    'домашний': 'домашний',
    'dwarf': 'карликовый',
    'карликовый': 'карликовый',
    'holland_lop': 'голландский вислоухий',
    'голландский': 'голландский',
    'angora': 'ангорский',
    'ангорский': 'ангорский',
    'rex': 'рекс',
    'рекс': 'рекс',
    'flemish': 'фламандский гигант',
    'фламандский': 'фламандский гигант'
}

# Породы грызунов
RODENT_BREEDS = {
    'hamster': 'хомяк',
    'хомяк': 'хомяк',
    'syrian': 'сирийский хомяк',
    'сирийский': 'сирийский хомяк',
    'dwarf_hamster': 'джунгарский хомяк',
    'джунгарский': 'джунгарский хомяк',
    'rat': 'крыса',
    'крыса': 'крыса',
    'mouse': 'мышь',
    'мышь': 'мышь',
    'gerbil': 'песчанка',
    'песчанка': 'песчанка',
    'guinea_pig': 'морская свинка',
    'морская_свинка': 'морская свинка',
    'chinchilla': 'шиншилла',
    'шиншилла': 'шиншилла'
}

# Цвета для определения по имени файла
COLORS = {
    'black': 'черный',
    'черный': 'черный',
    'white': 'белый', 
    'белый': 'белый',
    'gray': 'серый',
    'серый': 'серый',
    'grey': 'серый',
    'brown': 'коричневый',
    'коричневый': 'коричневый',
    'red': 'рыжий',
    'рыжий': 'рыжий',
    'orange': 'оранжевый',
    'оранжевый': 'оранжевый',
    'golden': 'золотистый',
    'золотистый': 'золотистый',
    'yellow': 'желтый',
    'желтый': 'желтый',
    'cream': 'кремовый',
    'кремовый': 'кремовый',
    'blue': 'голубой',
    'голубой': 'голубой',
    'tabby': 'табби',
    'табби': 'табби',
    'spotted': 'пятнистый',
    'пятнистый': 'пятнистый',
    'striped': 'полосатый',
    'полосатый': 'полосатый',
    'tuxedo': 'смокинг',
    'смокинг': 'смокинг',
    'calico': 'трехцветный',
    'трехцветный': 'трехцветный',
    'tricolor': 'трехцветный'
}

def detect_breed_from_filename(filename: str, animal_type: str) -> str:
    """Определяет породу животного по имени файла"""
    filename = filename.lower()
    
    if animal_type == "dog":
        for keyword, breed in DOG_BREEDS.items():
            if keyword in filename:
                return breed
        return "беспородная"
    
    elif animal_type == "cat":
        for keyword, breed in CAT_BREEDS.items():
            if keyword in filename:
                return breed
        return "домашняя"
    
    elif animal_type == "bird":
        for keyword, breed in BIRD_BREEDS.items():
            if keyword in filename:
                return breed
        return "беспородная"
    
    elif animal_type == "rabbit":
        for keyword, breed in RABBIT_BREEDS.items():
            if keyword in filename:
                return breed
        return "беспородная"
    
    elif animal_type == "rodent":
        for keyword, breed in RODENT_BREEDS.items():
            if keyword in filename:
                return breed
        return "беспородная"
    
    return "неизвестно"

def detect_color_from_filename(filename: str) -> str:
    """Определяет цвет животного по имени файла"""
    filename = filename.lower()
    
    for keyword, color in COLORS.items():
        if keyword in filename:
            return color
    
    # Базовые цвета по типу животного
    if "cat" in filename or "кот" in filename:
        return "серый"
    elif "dog" in filename or "собак" in filename:
        return "коричневый"
    
    return "смешанный"

def get_lost_pets_by_type(animal_type: str, special_features: List[str] = None, analysis_breed: str = None, analysis_color: str = None) -> List[Dict]:
    """Простой поиск объявлений о потерянных питомцах с вычислением сходства"""
    try:
        logger.info(f"Поиск объявлений: animal_type='{animal_type}', special_features={special_features}")
        
        with psycopg2.connect(
            host="localhost",
            port=5432,
            database="postgres",
            user="postgres",
            password="postgres",
            cursor_factory=psycopg2.extras.RealDictCursor
        ) as conn:
            with conn.cursor() as cursor:
                # Базовый запрос
                base_query = """
                    SELECT id, title, description, type as animal_type, breed, color, 
                           special_features as features, photo as image_url, created_at as lost_date, 
                           latitude as lost_location_lat, longitude as lost_location_lon, 
                           location as lost_location_address, author as contact_name, 
                           phone as contact_phone, status, created_at, updated_at
                    FROM advertisements_advertisement 
                    WHERE status = %s AND type = %s
                """
                
                # Если есть особенности, делаем два запроса: с особенностями и без них
                all_advertisements = []
                
                if special_features:
                    # Первый запрос: ищем объявления с особенностями в описании
                    like_conditions = []
                    special_params = ['lost', animal_type]
                    
                    for feature in special_features:
                        like_conditions.append("description ILIKE %s")
                        special_params.append(f"%{feature}%")
                    
                    if like_conditions:
                        special_query = f"{base_query} AND ({' OR '.join(like_conditions)})"
                        cursor.execute(special_query, special_params)
                        special_rows = cursor.fetchall()
                        logger.info(f"🎯 Найдено {len(special_rows)} объявлений с особенностями")
                        all_advertisements.extend(special_rows)
                
                # Всегда делаем основной запрос для получения всех объявлений типа
                cursor.execute(base_query, ['lost', animal_type])
                base_rows = cursor.fetchall()
                logger.info(f"📋 Найдено {len(base_rows)} обычных объявлений")
                
                # Добавляем обычные объявления, избегая дубликатов
                existing_ids = {row['id'] for row in all_advertisements}
                for row in base_rows:
                    if row['id'] not in existing_ids:
                        all_advertisements.append(row)
                
                logger.info(f"✅ Итого объявлений для обработки: {len(all_advertisements)}")
                
                # Простое преобразование в нужный формат
                advertisements = []
                for row in all_advertisements:
                    # Вычисляем сходство и тип совпадения
                    similarity, match_type = calculate_similarity_and_match_type(
                        row, analysis_breed, analysis_color, special_features
                    )
                    
                    ad = {
                        'id': str(row['id']),
                        'title': row['title'],
                        'description': row['description'],
                        'animal_type': row['animal_type'],
                        'breed': row['breed'] or 'unknown',
                        'color': row['color'] or 'unknown',
                        'pattern': 'solid',
                        'features': [row['features']] if row['features'] else [],
                        'image_url': row['image_url'],
                        'lost_date': row['lost_date'].isoformat() if row['lost_date'] else None,
                        'lost_location': {
                            'latitude': float(row['lost_location_lat']) if row['lost_location_lat'] else 0.0,
                            'longitude': float(row['lost_location_lon']) if row['lost_location_lon'] else 0.0,
                            'address': row['lost_location_address'] or ''
                        },
                        'contact': {
                            'name': row['contact_name'] or '',
                            'phone': row['contact_phone'] or '',
                            'email': ''
                        },
                        'reward': None,
                        'status': row['status'],
                        'created_at': row['created_at'].isoformat() if row['created_at'] else None,
                        'updated_at': row['updated_at'].isoformat() if row['updated_at'] else None,
                        'similarity': similarity,
                        'match_type': match_type
                    }
                    advertisements.append(ad)
                
                # Сортируем по сходству, потом по дате создания
                advertisements.sort(key=lambda x: (-x['similarity'], x['created_at'] or ''), reverse=False)
                return advertisements
                
    except Exception as e:
        logger.error(f"Ошибка при получении объявлений: {str(e)}")
        return []

def calculate_similarity_and_match_type(row, analysis_breed: str, analysis_color: str, special_features: List[str]) -> tuple:
    """Вычисляет сходство и тип совпадения"""
    import random
    
    similarity = 0.0
    match_type = 'type_match'  # по умолчанию - совпадение типа
    visual_similarity_detected = False
    
    # Базовое сходство за тип животного
    similarity += 0.4
    
    # Проверяем наличие уникальных особенностей в загруженном изображении
    has_unique_features = bool(special_features)
    
    # Особые признаки дают большой бонус и приоритет
    if special_features:
        logger.info(f"🔍 Обнаружены уникальные особенности: {special_features}")
        
        # Ищем совпадения в разных полях объявления
        search_text = f"{row['description']} {row['title']} {row.get('special_features', '')}".lower()
        
        feature_keywords = {
            'гетерохромия': ['гетерохромия', 'разные глаза', 'different eyes', 'heterochromia'],
            'залом на ухе': ['залом', 'ухо', 'ear fold', 'fold', 'сломанное ухо', 'травма уха'],
            'нет глаза': ['нет глаза', 'без глаза', 'missing eye', 'один глаз', 'слепой']
        }
        
        for feature in special_features:
            if feature in feature_keywords:
                keywords = feature_keywords[feature]
                if any(keyword in search_text for keyword in keywords):
                    similarity += 0.35  # Большой бонус за точное совпадение уникальной особенности
                    visual_similarity_detected = True
                    logger.info(f"✅ Найдено точное совпадение для '{feature}'")
                    break
        
        # Даже если не нашли точное совпадение, но есть уникальные особенности - даем бонус
        if not visual_similarity_detected:
            similarity += 0.25  # Средний бонус за наличие уникальных особенностей
            visual_similarity_detected = True
            logger.info(f"⭐ Бонус за уникальные особенности: {special_features}")
    
    # Устанавливаем тип совпадения с приоритетом визуального сходства
    if visual_similarity_detected:
        match_type = 'visual_similarity'
    else:
        # Бонус за породу (только если нет visual_similarity)
        if analysis_breed and row['breed']:
            if analysis_breed.lower() == row['breed'].lower():
                similarity += 0.4
                match_type = 'breed_match'
            elif 'беспородная' in analysis_breed.lower() or 'unknown' in analysis_breed.lower():
                similarity += 0.15
            else:
                # Добавляем небольшой случайный элемент для разнообразия
                similarity += random.uniform(0.05, 0.2)
        
        # Бонус за цвет (только если нет visual_similarity и breed_match)
        if analysis_color and row['color'] and match_type != 'breed_match':
            if analysis_color.lower() == row['color'].lower():
                similarity += 0.2
                if match_type == 'type_match':
                    match_type = 'color_match'
            else:
                similarity += random.uniform(0.0, 0.1)
    
    # Добавляем случайность для реалистичности (меньше для visual_similarity)
    if visual_similarity_detected:
        similarity += random.uniform(-0.05, 0.05)  # Меньше случайности для уникальных особенностей
    else:
        similarity += random.uniform(-0.1, 0.1)
    
    # Ограничиваем значения (для visual_similarity минимум выше)
    min_similarity = 0.6 if visual_similarity_detected else 0.3
    similarity = max(min_similarity, min(1.0, similarity))
    
    return round(similarity, 2), match_type

@app.get("/")
async def health_check():
    """Проверка работоспособности сервиса"""
    return {"status": "ok", "message": "ML service is running"}

@app.post("/search/")
async def search_pets(
    file: UploadFile = File(...),
    latitude: Optional[float] = Query(None, description="Широта для поиска похожих объявлений"),
    longitude: Optional[float] = Query(None, description="Долгота для поиска похожих объявлений"),
    radius_km: Optional[float] = Query(10.0, description="Радиус поиска в километрах")
) -> SearchResponse:
    """Псевдо-анализ изображения и поиск похожих питомцев по имени файла"""
    try:
        filename = file.filename.lower()
        content = await file.read()  # читаем, чтобы не было ошибок, но не используем

        logger.info(f"Анализируем файл: '{filename}'")  # DEBUG

        # Определяем тип животного по имени файла
        if "cat" in filename or "кот" in filename or "кошк" in filename:
            animal_type = "cat"
        elif "dog" in filename or "собак" in filename or "пес" in filename or "щенок" in filename:
            animal_type = "dog"
        elif "bird" in filename or "птиц" in filename or "голубь" in filename or "попугай" in filename or "канарейка" in filename:
            animal_type = "bird"
        elif "rabbit" in filename or "кролик" in filename or "заяц" in filename:
            animal_type = "rabbit"
        elif "hamster" in filename or "хомяк" in filename or "крыса" in filename or "мышь" in filename:
            animal_type = "rodent"
        else:
            animal_type = "unknown"

        # Определяем породу и цвет с помощью новых функций
        breed = detect_breed_from_filename(filename, animal_type)
        color = detect_color_from_filename(filename)
        
        # Определяем паттерн
        if any(word in filename for word in ['spotted', 'пятнистый']):
            pattern = "spotted"
        elif any(word in filename for word in ['striped', 'полосатый', 'tabby', 'табби']):
            pattern = "striped"
        elif any(word in filename for word in ['tuxedo', 'смокинг']):
            pattern = "tuxedo"
        else:
            pattern = "solid"

        # Уникальные метрики по ключевым словам (улучшенное обнаружение)
        unique_features = {
            'heterochromia': {'present': False, 'confidence': 0.0},
            'ear_fold': {'present': False, 'confidence': 0.0},
            'missing_eye': {'present': False, 'confidence': 0.0},
            'flat_face': {'present': False, 'confidence': 0.0},
            'short_tail': {'present': False, 'confidence': 0.0}
        }
        
        special_features = []
        
        # Гетерохромия - расширенный поиск
        heterochromia_keywords = [
            'гетерохромия', 'heterochromia', 'разные_глаза', 'different_eyes', 
            'разноцветные_глаза', 'multicolor_eyes', 'мультиколор'
        ]
        if any(keyword in filename for keyword in heterochromia_keywords):
            unique_features['heterochromia'] = {'present': True, 'confidence': 1.0}
            special_features.append('гетерохромия')
            logger.info(f"🔍 Обнаружена гетерохромия в файле: {filename}")
            
        # Залом на ухе - расширенный поиск
        ear_fold_keywords = [
            'залом', 'ear_fold', 'fold', 'сломанное_ухо', 'травма_уха',
            'деформация_уха', 'поврежденное_ухо', 'кривое_ухо'
        ]
        if any(keyword in filename for keyword in ear_fold_keywords):
            unique_features['ear_fold'] = {'present': True, 'confidence': 1.0}
            special_features.append('залом на ухе')
            logger.info(f"🔍 Обнаружен залом на ухе в файле: {filename}")
            
        # Отсутствие глаза - расширенный поиск
        missing_eye_keywords = [
            'нет_глаза', 'без_глаза', 'no_eye', 'missing_eye', 'один_глаз', 
            'слепой', 'blind', 'потерял_глаз', 'травма_глаза'
        ]
        if any(keyword in filename for keyword in missing_eye_keywords):
            unique_features['missing_eye'] = {'present': True, 'confidence': 1.0}
            special_features.append('нет глаза')
            logger.info(f"🔍 Обнаружено отсутствие глаза в файле: {filename}")
        
        # Добавляем дополнительные особенности
        if 'плоская_морда' in filename or 'flat_face' in filename:
            unique_features['flat_face'] = {'present': True, 'confidence': 1.0}
            special_features.append('плоская морда')
            logger.info(f"🔍 Обнаружена плоская морда в файле: {filename}")
            
        if 'короткий_хвост' in filename or 'short_tail' in filename or 'без_хвоста' in filename:
            unique_features['short_tail'] = {'present': True, 'confidence': 1.0}
            special_features.append('короткий хвост')
            logger.info(f"🔍 Обнаружен короткий хвост в файле: {filename}")
        
        if special_features:
            logger.info(f"✅ Итого обнаружено уникальных особенностей: {special_features}")

        # Формируем features с учетом найденных особенностей
        features_list = [{'label': 'pseudo', 'confidence': 1.0}]
        if special_features:
            for feature in special_features:
                features_list.append({'label': feature, 'confidence': 1.0})

        # Формируем analysis
        structured_analysis = {
            'animal_type': {'label': animal_type, 'confidence': 1.0 if animal_type != 'unknown' else 0.0},
            'breed': {'label': breed, 'confidence': 1.0 if breed != 'unknown' else 0.0},
            'color': {'label': color, 'confidence': 0.9, 'pattern': pattern},
            'features': features_list,
            'confidence': 1.0 if animal_type != 'unknown' else 0.0,
            'body_proportions': {'aspect_ratio': 1.0, 'compactness': 0.7, 'size_category': 'medium'},
            'unique_features': unique_features
        }

        # Получаем объявления из PostgreSQL
        similar_lost_pets = get_lost_pets_by_type(animal_type, special_features, breed, color)
        
        logger.info(f"Найдено {len(similar_lost_pets)} объявлений для '{animal_type}'")

        response = SearchResponse(
            analysis=ImageAnalysis(**structured_analysis),
            similar_pets=[],
            similar_lost_pets=similar_lost_pets
        )
        return response
    except Exception as e:
        logger.error(f"Ошибка в псевдо-анализаторе: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    print("Запуск ML сервиса...")
    uvicorn.run(app, host="0.0.0.0", port=5004) 