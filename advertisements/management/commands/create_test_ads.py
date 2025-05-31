from django.core.management.base import BaseCommand
from advertisements.models import Advertisement
from django.utils import timezone
from django.core.files.base import ContentFile
import requests
from PIL import Image
import io
import random

class Command(BaseCommand):
    help = 'Creates test advertisements with sample pet images'

    def handle(self, *args, **kwargs):
        # Список тестовых объявлений с разными характеристиками
        test_ads = [
            {
                'title': 'Потерялся рыжий кот Барсик',
                'description': 'Рыжий кот с белыми лапками, очень дружелюбный. Потерялся в районе ТРЦ "Гринвич". Откликается на имя Барсик.',
                'author': 'Анна Петрова',
                'breed': 'Домашний',
                'type': 'cat',
                'status': 'lost',
                'color': 'red',
                'sex': 'male',
                'eye_color': 'yellow',
                'face_shape': 'round',
                'special_features': 'none',
                'latitude': 56.836341,
                'longitude': 60.594635,
                'location': 'ТРЦ Гринвич, Екатеринбург',
                'phone': '+79123456789'
            },
            {
                'title': 'Найдена белая собака в Академическом',
                'description': 'Найдена белая собака породы самоед, ошейник синий. Очень добрая и ухоженная.',
                'author': 'Михаил Иванов',
                'breed': 'Самоед',
                'type': 'dog',
                'status': 'found',
                'color': 'white',
                'sex': 'female',
                'eye_color': 'brown',
                'face_shape': 'oval',
                'special_features': 'none',
                'latitude': 56.783965,
                'longitude': 60.543880,
                'location': 'Академический район, Екатеринбург',
                'phone': '+79234567890'
            },
            {
                'title': 'Пропала черная кошка Мурка',
                'description': 'Черная кошка с желтыми глазами. Стерилизована, очень ласковая.',
                'author': 'Елена Сидорова',
                'breed': 'Домашняя',
                'type': 'cat',
                'status': 'lost',
                'color': 'black',
                'sex': 'female',
                'eye_color': 'yellow',
                'face_shape': 'triangular',
                'special_features': 'none',
                'latitude': 56.843893,
                'longitude': 60.645943,
                'location': 'Центр, Екатеринбург',
                'phone': '+79345678901'
            },
            {
                'title': 'Найден серый кот с белыми пятнами',
                'description': 'Серый кот с белыми пятнами на груди и лапах. Кастрирован.',
                'author': 'Дмитрий Козлов',
                'breed': 'Британская короткошерстная',
                'type': 'cat',
                'status': 'found',
                'color': 'gray',
                'sex': 'male',
                'eye_color': 'blue',
                'face_shape': 'round',
                'special_features': 'spotted_pattern',
                'latitude': 56.838011,
                'longitude': 60.597465,
                'location': 'Уралмаш, Екатеринбург',
                'phone': '+79456789012'
            },
            {
                'title': 'Потерялась собака породы лабрадор',
                'description': 'Золотистый лабрадор, очень дружелюбный. Носит красный ошейник.',
                'author': 'Ольга Морозова',
                'breed': 'Лабрадор',
                'type': 'dog',
                'status': 'lost',
                'color': 'golden',
                'sex': 'male',
                'eye_color': 'brown',
                'face_shape': 'oval',
                'special_features': 'none',
                'latitude': 56.832425,
                'longitude': 60.605702,
                'location': 'Ботаника, Екатеринбург',
                'phone': '+79567890123'
            },
            {
                'title': 'Найден пятнистый кот бенгальской породы',
                'description': 'Бенгальский кот с красивыми пятнами. Очень активный и игривый.',
                'author': 'Александр Новиков',
                'breed': 'Бенгальская',
                'type': 'cat',
                'status': 'found',
                'color': 'spotted',
                'sex': 'male',
                'eye_color': 'green',
                'face_shape': 'triangular',
                'special_features': 'spotted_pattern',
                'latitude': 56.850123,
                'longitude': 60.612345,
                'location': 'Пионерский, Екатеринбург',
                'phone': '+79678901234'
            },
            {
                'title': 'Пропала трехцветная кошка',
                'description': 'Трехцветная кошка (черный, белый, рыжий). Очень пугливая.',
                'author': 'Мария Волкова',
                'breed': 'Домашняя',
                'type': 'cat',
                'status': 'lost',
                'color': 'multicolor',
                'sex': 'female',
                'eye_color': 'yellow',
                'face_shape': 'round',
                'special_features': 'none',
                'latitude': 56.825678,
                'longitude': 60.590123,
                'location': 'Эльмаш, Екатеринбург',
                'phone': '+79789012345'
            },
            {
                'title': 'Найдена собака с разными глазами',
                'description': 'Хаски с гетерохромией (один глаз голубой, другой карий).',
                'author': 'Игорь Лебедев',
                'breed': 'Сибирский хаски',
                'type': 'dog',
                'status': 'found',
                'color': 'gray',
                'sex': 'female',
                'eye_color': 'different',
                'face_shape': 'triangular',
                'special_features': 'heterochromia',
                'latitude': 56.815432,
                'longitude': 60.575678,
                'location': 'Химмаш, Екатеринбург',
                'phone': '+79890123456'
            }
        ]

        created_count = 0
        
        for ad_data in test_ads:
            # Проверяем, не существует ли уже такое объявление
            if not Advertisement.objects.filter(title=ad_data['title']).exists():
                try:
                    # Создаем объявление
                    ad = Advertisement.objects.create(**ad_data)
                    created_count += 1
                    self.stdout.write(
                        self.style.SUCCESS(f'Создано объявление: {ad.title}')
                    )
                except Exception as e:
                    self.stdout.write(
                        self.style.ERROR(f'Ошибка при создании объявления {ad_data["title"]}: {str(e)}')
                    )
            else:
                self.stdout.write(
                    self.style.WARNING(f'Объявление уже существует: {ad_data["title"]}')
                )

        self.stdout.write(
            self.style.SUCCESS(f'Создано {created_count} новых объявлений')
        ) 