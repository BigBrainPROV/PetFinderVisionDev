from django.core.management.base import BaseCommand
from django.core.files import File
from django.contrib.auth.models import User
from advertisements.models import Advertisement
from datetime import datetime
import os
from pathlib import Path

class Command(BaseCommand):
    help = 'Добавляет тестовые данные в базу данных'

    def handle(self, *args, **options):
        self.stdout.write('Начинаем добавление тестовых данных...')

        # Создаем тестового пользователя
        user, created = User.objects.get_or_create(
            username='test_user',
            defaults={
                'email': 'test@example.com',
                'is_active': True
            }
        )
        if created:
            user.set_password('testpass123')
            user.save()
            self.stdout.write(self.style.SUCCESS('Создан тестовый пользователь'))

        # Тестовые данные для объявлений
        test_ads = [
            {
                'title': 'Потерялся рыжий кот',
                'description': 'Потерялся рыжий кот с белыми лапками. Очень дружелюбный.',
                'type': 'cat',
                'breed': 'дворовый',
                'color': 'red',
                'status': 'lost',
                'photo': 'test_images/cat1.jpg',
                'author': 'test_user'
            },
            {
                'title': 'Найден черно-белый кот',
                'description': 'Найден черно-белый кот в районе центрального парка.',
                'type': 'cat',
                'breed': 'дворовый',
                'color': 'black',
                'status': 'found',
                'photo': 'test_images/cat2.jpg',
                'author': 'test_user'
            },
            {
                'title': 'Потерялась собака породы хаски',
                'description': 'Потерялась собака породы хаски, серо-белого окраса.',
                'type': 'dog',
                'breed': 'хаски',
                'color': 'gray',
                'status': 'lost',
                'photo': 'test_images/dog1.jpg',
                'author': 'test_user'
            },
            {
                'title': 'Найдена собака породы лабрадор',
                'description': 'Найдена собака породы лабрадор, золотистого окраса.',
                'type': 'dog',
                'breed': 'лабрадор',
                'color': 'golden',
                'status': 'found',
                'photo': 'test_images/dog2.jpg',
                'author': 'test_user'
            }
        ]

        # Создаем объявления
        for ad_data in test_ads:
            ad = Advertisement.objects.create(
                author=ad_data['author'],
                title=ad_data['title'],
                description=ad_data['description'],
                type=ad_data['type'],
                breed=ad_data['breed'],
                color=ad_data['color'],
                status=ad_data['status'],
                created_at=datetime.now()
            )
            
            # Добавляем фото
            photo_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__)))), ad_data['photo'])
            if os.path.exists(photo_path):
                with open(photo_path, 'rb') as f:
                    ad.photo.save(os.path.basename(photo_path), File(f), save=True)
                self.stdout.write(self.style.SUCCESS(f'Добавлено объявление: {ad_data["title"]}'))
            else:
                self.stdout.write(self.style.WARNING(f'Фото не найдено: {photo_path}'))

        self.stdout.write(self.style.SUCCESS('Тестовые данные успешно добавлены!')) 