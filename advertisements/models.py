from django.db import models
from django.utils import timezone

from common.validators import phone_regex


class AnimalTypeChoices(models.TextChoices):
    CAT = 'cat', 'Кошка'
    DOG = 'dog', 'Собака'
    BIRD = 'bird', 'Птица'
    RODENT = 'rodent', 'Грызун'
    RABBIT = 'rabbit', 'Кролик'
    REPTILE = 'reptile', 'Рептилия'
    OTHER = 'other', 'Другое животное'


class ColorChoices(models.TextChoices):
    WHITE = 'white', 'Белый'
    BLACK = 'black', 'Черный'
    GRAY = 'gray', 'Серый'
    LIGHT_GRAY = 'light_gray', 'Светло-серый'
    DARK_GRAY = 'dark_gray', 'Темно-серый'
    BROWN = 'brown', 'Коричневый'
    RED = 'red', 'Рыжий'
    ORANGE = 'orange', 'Оранжевый'
    YELLOW = 'yellow', 'Желтый'
    GOLDEN = 'golden', 'Золотистый'
    GREEN = 'green', 'Зеленый'
    BLUE = 'blue', 'Голубой'
    PURPLE = 'purple', 'Фиолетовый'
    MULTICOLOR = 'multicolor', 'Многоцветный'
    SPOTTED = 'spotted', 'Пятнистый'
    STRIPED = 'striped', 'Полосатый'
    TUXEDO = 'tuxedo', 'Смокинг'


class SexChoices(models.TextChoices):
    MALE = 'male', 'Мальчик'
    FEMALE = 'female', 'Девочка'
    UNKNOWN = 'unknown', 'Неизвестно'


class EyeColorChoices(models.TextChoices):
    BLUE = 'blue', 'Голубые'
    GREEN = 'green', 'Зеленые'
    YELLOW = 'yellow', 'Желтые'
    BROWN = 'brown', 'Карие'
    BLACK = 'black', 'Черные'
    RED = 'red', 'Красные'
    DIFFERENT = 'different', 'Разные'
    AMBER = 'amber', 'Янтарные'
    HAZEL = 'hazel', 'Ореховые'


class FaceShapeChoices(models.TextChoices):
    ROUND = 'round', 'Круглая'
    OVAL = 'oval', 'Овальная'
    TRIANGULAR = 'triangular', 'Треугольная'
    LONG = 'long', 'Вытянутая'
    FLAT = 'flat', 'Плоская'
    SQUARE = 'square', 'Квадратная'
    OTHER = 'other', 'Другая'


class SpecialFeatures(models.TextChoices):
    HETEROCHROMIA = 'heterochromia', 'Гетерохромия'
    EAR_FOLD = 'ear_fold', 'Залом на ухе'
    EYE_SPOT = 'eye_spot', 'Пятно на глазу'
    MISSING_EYE = 'missing_eye', 'Нет глазика'
    TAIL_MISSING = 'tail_missing', 'Отсутствует хвост'
    LIMB_MISSING = 'limb_missing', 'Отсутствует лапка'
    ALBINO = 'albino', 'Альбинизм'
    VITILIGO = 'vitiligo', 'Витилиго'
    SPOTTED_PATTERN = 'spotted_pattern', 'Пятнистый узор'
    STRIPED_PATTERN = 'striped_pattern', 'Полосатый узор'
    FLUFFY_COAT = 'fluffy_coat', 'Пушистая шерсть'
    CURLY_COAT = 'curly_coat', 'Кудрявая шерсть'
    SCAR = 'scar', 'Шрам'
    COLLAR = 'collar', 'Ошейник'
    NONE = 'none', 'Нет особых примет'


class SizeChoices(models.TextChoices):
    TINY = 'tiny', 'Очень маленький'
    SMALL = 'small', 'Маленький'
    MEDIUM = 'medium', 'Средний'
    LARGE = 'large', 'Большой'
    EXTRA_LARGE = 'extra_large', 'Очень большой'


class CoatTypeChoices(models.TextChoices):
    SHORT = 'short', 'Короткошерстный'
    MEDIUM = 'medium', 'Среднешерстный'
    LONG = 'long', 'Длинношерстный'
    CURLY = 'curly', 'Кудрявый'
    WIRE = 'wire', 'Жесткошерстный'
    HAIRLESS = 'hairless', 'Бесшерстный'


class BodyTypeChoices(models.TextChoices):
    COMPACT = 'compact', 'Компактное'
    NORMAL = 'normal', 'Нормальное'
    ELONGATED = 'elongated', 'Вытянутое'
    MUSCULAR = 'muscular', 'Мускулистое'
    SLIM = 'slim', 'Стройное'


class StatusChoices(models.TextChoices):
    LOST = 'lost', 'Потерян'
    FOUND = 'found', 'Найден'


class Advertisement(models.Model):
    # Основная информация
    title = models.CharField(max_length=255, verbose_name='Заголовок')
    description = models.TextField(verbose_name='Описание')
    author = models.CharField(max_length=255, verbose_name='Автор')
    photo = models.ImageField(upload_to='advertisements/', verbose_name='Фото', null=True, blank=True)
    phone = models.CharField(
        validators=[phone_regex],
        max_length=15,
        null=True,
        blank=True,
        verbose_name="phone",
    )
    
    # Базовые характеристики
    breed = models.CharField(max_length=255, verbose_name='Порода')
    color = models.CharField(
        max_length=20,
        choices=ColorChoices.choices,
        default=ColorChoices.WHITE,
        verbose_name='Цвет'
    )
    sex = models.CharField(
        max_length=10,
        choices=SexChoices.choices,
        default=SexChoices.UNKNOWN,
        verbose_name='Пол'
    )
    type = models.CharField(
        max_length=20,
        choices=AnimalTypeChoices.choices,
        default=AnimalTypeChoices.CAT,
        verbose_name='Тип животного'
    )
    
    # Физические характеристики
    eye_color = models.CharField(
        max_length=20,
        choices=EyeColorChoices.choices,
        default=EyeColorChoices.YELLOW,
        verbose_name='Цвет глаз'
    )
    face_shape = models.CharField(
        max_length=20,
        choices=FaceShapeChoices.choices,
        default=FaceShapeChoices.ROUND,
        verbose_name='Форма мордочки'
    )
    special_features = models.CharField(
        max_length=20,
        choices=SpecialFeatures.choices,
        default=SpecialFeatures.NONE,
        verbose_name='Особые приметы'
    )
    
    # Новые расширенные характеристики
    size = models.CharField(
        max_length=20,
        choices=SizeChoices.choices,
        default=SizeChoices.MEDIUM,
        verbose_name='Размер',
        null=True,
        blank=True
    )
    coat_type = models.CharField(
        max_length=20,
        choices=CoatTypeChoices.choices,
        default=CoatTypeChoices.SHORT,
        verbose_name='Тип шерсти',
        null=True,
        blank=True
    )
    body_type = models.CharField(
        max_length=20,
        choices=BodyTypeChoices.choices,
        default=BodyTypeChoices.NORMAL,
        verbose_name='Тип телосложения',
        null=True,
        blank=True
    )
    
    # Уникальные метрики (автоматически заполняются ИИ)
    fluffiness_score = models.FloatField(
        verbose_name='Коэффициент пушистости',
        null=True,
        blank=True,
        help_text='От 0.0 до 1.0, определяется автоматически'
    )
    symmetry_score = models.FloatField(
        verbose_name='Коэффициент симметрии',
        null=True,
        blank=True,
        help_text='От 0.0 до 1.0, определяется автоматически'
    )
    pattern_complexity = models.FloatField(
        verbose_name='Сложность узора',
        null=True,
        blank=True,
        help_text='Числовое значение, определяется автоматически'
    )
    body_proportions = models.FloatField(
        verbose_name='Пропорции тела',
        null=True,
        blank=True,
        help_text='Соотношение ширины к высоте'
    )
    color_diversity = models.IntegerField(
        verbose_name='Разнообразие цветов',
        null=True,
        blank=True,
        help_text='Количество основных цветов в окрасе'
    )
    
    # Дополнительные характеристики
    estimated_age = models.CharField(
        max_length=50,
        verbose_name='Примерный возраст',
        null=True,
        blank=True,
        help_text='Например: щенок, молодой, взрослый, пожилой'
    )
    weight_estimate = models.CharField(
        max_length=50,
        verbose_name='Примерный вес',
        null=True,
        blank=True,
        help_text='Например: до 5кг, 5-15кг, 15-30кг, более 30кг'
    )
    temperament = models.CharField(
        max_length=100,
        verbose_name='Характер',
        null=True,
        blank=True,
        help_text='Например: спокойный, игривый, агрессивный'
    )
    
    # Контактная информация и местоположение
    social_media = models.URLField(verbose_name='Социальные сети', null=True, blank=True)
    status = models.CharField(
        max_length=10,
        choices=StatusChoices.choices,
        default=StatusChoices.LOST,
        verbose_name='Статус'
    )
    latitude = models.FloatField(verbose_name='Широта', null=True, blank=True)
    longitude = models.FloatField(verbose_name='Долгота', null=True, blank=True)
    location = models.CharField(max_length=255, verbose_name='Адрес', null=True, blank=True)
    
    # Системные поля
    created_at = models.DateTimeField(default=timezone.now, verbose_name='Дата создания')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='Дата обновления')
    ai_analyzed = models.BooleanField(
        default=False,
        verbose_name='Проанализировано ИИ',
        help_text='Отмечается автоматически при анализе фото'
    )
    ai_confidence = models.FloatField(
        verbose_name='Уверенность ИИ',
        null=True,
        blank=True,
        help_text='Общая уверенность ИИ в анализе (0.0-1.0)'
    )

    def __str__(self):
        return f'{self.title}'

    class Meta:
        verbose_name = 'Объявление'
        verbose_name_plural = 'Объявления'
        ordering = ['-created_at']

    def get_unique_features_display(self):
        """Возвращает список уникальных особенностей питомца"""
        features = []
        
        if self.fluffiness_score and self.fluffiness_score > 0.7:
            features.append('Очень пушистый')
        elif self.fluffiness_score and self.fluffiness_score > 0.4:
            features.append('Пушистый')
            
        if self.symmetry_score and self.symmetry_score > 0.8:
            features.append('Симметричная мордочка')
            
        if self.pattern_complexity and self.pattern_complexity > 20:
            features.append('Сложный узор')
        elif self.pattern_complexity and self.pattern_complexity > 10:
            features.append('Узорчатый окрас')
            
        if self.color_diversity and self.color_diversity > 3:
            features.append('Многоцветный')
            
        if self.body_proportions:
            if self.body_proportions > 1.5:
                features.append('Вытянутое тело')
            elif self.body_proportions < 0.8:
                features.append('Компактное тело')
                
        return features

    def get_ai_analysis_summary(self):
        """Возвращает краткое описание ИИ-анализа"""
        if not self.ai_analyzed:
            return "Не анализировалось ИИ"
            
        confidence_text = "высокая" if self.ai_confidence and self.ai_confidence > 0.8 else \
                         "средняя" if self.ai_confidence and self.ai_confidence > 0.5 else "низкая"
                         
        unique_features = self.get_unique_features_display()
        features_text = ", ".join(unique_features) if unique_features else "стандартные характеристики"
        
        return f"Уверенность: {confidence_text}, особенности: {features_text}"
