from django.core.management.base import BaseCommand
from advertisements.models import Advertisement
from django.utils import timezone
import random

class Command(BaseCommand):
    help = 'Creates additional test advertisements for training'

    def handle(self, *args, **kwargs):
        # Дополнительные тестовые объявления
        additional_ads = [
            {
                'title': 'Потерялся персидский кот Пушок',
                'description': 'Длинношерстный персидский кот, белый с серыми пятнами.',
                'author': 'Татьяна Смирнова',
                'breed': 'Персидская',
                'type': 'cat',
                'status': 'lost',
                'color': 'white',
                'sex': 'male',
                'eye_color': 'blue',
                'face_shape': 'round',
                'special_features': 'none',
                'latitude': 56.840000,
                'longitude': 60.600000,
                'location': 'Верх-Исетский район, Екатеринбург',
                'phone': '+79111111111'
            },
            {
                'title': 'Найдена собака породы овчарка',
                'description': 'Немецкая овчарка, коричнево-черная, очень умная.',
                'author': 'Сергей Петров',
                'breed': 'Немецкая овчарка',
                'type': 'dog',
                'status': 'found',
                'color': 'brown',
                'sex': 'female',
                'eye_color': 'brown',
                'face_shape': 'triangular',
                'special_features': 'none',
                'latitude': 56.845000,
                'longitude': 60.605000,
                'location': 'Кировский район, Екатеринбург',
                'phone': '+79222222222'
            },
            {
                'title': 'Пропал сиамский кот Симба',
                'description': 'Сиамский кот с голубыми глазами, очень ласковый.',
                'author': 'Наталья Козлова',
                'breed': 'Сиамская',
                'type': 'cat',
                'status': 'lost',
                'color': 'brown',
                'sex': 'male',
                'eye_color': 'blue',
                'face_shape': 'triangular',
                'special_features': 'none',
                'latitude': 56.850000,
                'longitude': 60.610000,
                'location': 'Ленинский район, Екатеринбург',
                'phone': '+79333333333'
            },
            {
                'title': 'Найден рыжий кот с зелеными глазами',
                'description': 'Рыжий кот, очень дружелюбный, зеленые глаза.',
                'author': 'Владимир Иванов',
                'breed': 'Домашний',
                'type': 'cat',
                'status': 'found',
                'color': 'red',
                'sex': 'male',
                'eye_color': 'green',
                'face_shape': 'round',
                'special_features': 'none',
                'latitude': 56.835000,
                'longitude': 60.595000,
                'location': 'Октябрьский район, Екатеринбург',
                'phone': '+79444444444'
            },
            {
                'title': 'Потерялась собака породы спаниель',
                'description': 'Кокер-спаниель, золотистого цвета, очень добрая.',
                'author': 'Людмила Федорова',
                'breed': 'Кокер-спаниель',
                'type': 'dog',
                'status': 'lost',
                'color': 'golden',
                'sex': 'female',
                'eye_color': 'brown',
                'face_shape': 'oval',
                'special_features': 'none',
                'latitude': 56.830000,
                'longitude': 60.590000,
                'location': 'Чкаловский район, Екатеринбург',
                'phone': '+79555555555'
            },
            {
                'title': 'Найден черный кот с белой грудкой',
                'description': 'Черный кот с белым пятном на груди, кастрирован.',
                'author': 'Андрей Соколов',
                'breed': 'Домашний',
                'type': 'cat',
                'status': 'found',
                'color': 'black',
                'sex': 'male',
                'eye_color': 'yellow',
                'face_shape': 'round',
                'special_features': 'none',
                'latitude': 56.825000,
                'longitude': 60.585000,
                'location': 'Железнодорожный район, Екатеринбург',
                'phone': '+79666666666'
            },
            {
                'title': 'Пропала кошка породы мейн-кун',
                'description': 'Мейн-кун, серая с полосами, очень крупная.',
                'author': 'Екатерина Волкова',
                'breed': 'Мейн-кун',
                'type': 'cat',
                'status': 'lost',
                'color': 'gray',
                'sex': 'female',
                'eye_color': 'green',
                'face_shape': 'triangular',
                'special_features': 'none',
                'latitude': 56.855000,
                'longitude': 60.615000,
                'location': 'Орджоникидзевский район, Екатеринбург',
                'phone': '+79777777777'
            },
            {
                'title': 'Найдена собака породы бигль',
                'description': 'Бигль, трехцветный (белый, коричневый, черный).',
                'author': 'Максим Лебедев',
                'breed': 'Бигль',
                'type': 'dog',
                'status': 'found',
                'color': 'multicolor',
                'sex': 'male',
                'eye_color': 'brown',
                'face_shape': 'oval',
                'special_features': 'none',
                'latitude': 56.820000,
                'longitude': 60.580000,
                'location': 'Автовокзал, Екатеринбург',
                'phone': '+79888888888'
            },
            {
                'title': 'Потерялся белый кот с голубыми глазами',
                'description': 'Белый кот, возможно глухой, голубые глаза.',
                'author': 'Ирина Морозова',
                'breed': 'Домашний',
                'type': 'cat',
                'status': 'lost',
                'color': 'white',
                'sex': 'male',
                'eye_color': 'blue',
                'face_shape': 'round',
                'special_features': 'none',
                'latitude': 56.860000,
                'longitude': 60.620000,
                'location': 'Компрессорный, Екатеринбург',
                'phone': '+79999999999'
            },
            {
                'title': 'Найдена собака с купированными ушами',
                'description': 'Доберман, черный с рыжими подпалинами.',
                'author': 'Роман Новиков',
                'breed': 'Доберман',
                'type': 'dog',
                'status': 'found',
                'color': 'black',
                'sex': 'female',
                'eye_color': 'brown',
                'face_shape': 'triangular',
                'special_features': 'ear_fold',
                'latitude': 56.815000,
                'longitude': 60.575000,
                'location': 'Широкая речка, Екатеринбург',
                'phone': '+79000000000'
            },
            {
                'title': 'Пропал полосатый кот Тигр',
                'description': 'Полосатый серый кот с черными полосами.',
                'author': 'Галина Петрова',
                'breed': 'Домашний',
                'type': 'cat',
                'status': 'lost',
                'color': 'gray',
                'sex': 'male',
                'eye_color': 'yellow',
                'face_shape': 'round',
                'special_features': 'none',
                'latitude': 56.865000,
                'longitude': 60.625000,
                'location': 'Сортировка, Екатеринбург',
                'phone': '+79111222333'
            },
            {
                'title': 'Найдена собака породы йоркширский терьер',
                'description': 'Маленький йорк, очень активный и игривый.',
                'author': 'Светлана Козлова',
                'breed': 'Йоркширский терьер',
                'type': 'dog',
                'status': 'found',
                'color': 'brown',
                'sex': 'female',
                'eye_color': 'brown',
                'face_shape': 'round',
                'special_features': 'none',
                'latitude': 56.810000,
                'longitude': 60.570000,
                'location': 'Шарташ, Екатеринбург',
                'phone': '+79222333444'
            }
        ]

        created_count = 0
        
        for ad_data in additional_ads:
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
            self.style.SUCCESS(f'Создано {created_count} дополнительных объявлений')
        ) 