import os
import django
import sys
from django.core.files import File
from datetime import datetime

# Настройка Django
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'PetFinderVision.settings.dev_settings')
django.setup()

from advertisements.models import Advertisement
from django.contrib.auth.models import User

def create_test_data():
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

    # Тестовые данные для объявлений
    test_ads = [
        {
            'title': 'Потерялся рыжий кот',
            'description': 'Потерялся рыжий кот с белыми лапками. Очень дружелюбный.',
            'type': 'cat',
            'breed': 'дворовый',
            'color': 'рыжий',
            'status': 'lost',
            'photo': 'test_images/cat1.jpg'
        },
        {
            'title': 'Найден черно-белый кот',
            'description': 'Найден черно-белый кот в районе центрального парка.',
            'type': 'cat',
            'breed': 'дворовый',
            'color': 'черно-белый',
            'status': 'found',
            'photo': 'test_images/cat2.jpg'
        },
        {
            'title': 'Потерялась собака породы хаски',
            'description': 'Потерялась собака породы хаски, серо-белого окраса.',
            'type': 'dog',
            'breed': 'хаски',
            'color': 'серый',
            'status': 'lost',
            'photo': 'test_images/dog1.jpg'
        },
        {
            'title': 'Найдена собака породы лабрадор',
            'description': 'Найдена собака породы лабрадор, золотистого окраса.',
            'type': 'dog',
            'breed': 'лабрадор',
            'color': 'золотистый',
            'status': 'found',
            'photo': 'test_images/dog2.jpg'
        }
    ]

    # Создаем объявления
    for ad_data in test_ads:
        ad = Advertisement.objects.create(
            user=user,
            title=ad_data['title'],
            description=ad_data['description'],
            type=ad_data['type'],
            breed=ad_data['breed'],
            color=ad_data['color'],
            status=ad_data['status'],
            created_at=datetime.now()
        )
        
        # Добавляем фото
        photo_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), ad_data['photo'])
        if os.path.exists(photo_path):
            with open(photo_path, 'rb') as f:
                ad.photo.save(os.path.basename(photo_path), File(f), save=True)
        else:
            print(f"Warning: Photo not found at {photo_path}")

if __name__ == '__main__':
    create_test_data()
    print("Test data created successfully!") 