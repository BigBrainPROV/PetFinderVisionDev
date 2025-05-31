from django.core.management.base import BaseCommand
from django.contrib.auth.models import User


class Command(BaseCommand):
    help = 'Creates test users for development'

    def handle(self, *args, **kwargs):
        # Создаем суперпользователя
        if not User.objects.filter(username='admin').exists():
            admin_user = User.objects.create_superuser(
                username='admin',
                email='admin@petfinder.com',
                password='admin123'
            )
            self.stdout.write(
                self.style.SUCCESS(f'✅ Создан суперпользователь: admin (пароль: admin123)')
            )
        else:
            self.stdout.write(
                self.style.WARNING('⚠️ Суперпользователь admin уже существует')
            )

        # Создаем тестовых пользователей
        test_users = [
            {
                'username': 'testuser',
                'email': 'test@petfinder.com',
                'password': 'test123',
                'first_name': 'Тест',
                'last_name': 'Пользователь'
            },
            {
                'username': 'anna',
                'email': 'anna@petfinder.com', 
                'password': 'anna123',
                'first_name': 'Анна',
                'last_name': 'Петрова'
            },
            {
                'username': 'mikhail',
                'email': 'mikhail@petfinder.com',
                'password': 'mikhail123', 
                'first_name': 'Михаил',
                'last_name': 'Иванов'
            },
            {
                'username': 'elena',
                'email': 'elena@petfinder.com',
                'password': 'elena123',
                'first_name': 'Елена', 
                'last_name': 'Сидорова'
            }
        ]

        created_count = 0
        for user_data in test_users:
            username = user_data['username']
            if not User.objects.filter(username=username).exists():
                user = User.objects.create_user(**user_data)
                created_count += 1
                self.stdout.write(
                    self.style.SUCCESS(f'✅ Создан пользователь: {username} (пароль: {user_data["password"]})')
                )
            else:
                self.stdout.write(
                    self.style.WARNING(f'⚠️ Пользователь {username} уже существует')
                )

        self.stdout.write('')
        self.stdout.write(self.style.SUCCESS(f'🎉 Создано {created_count} новых пользователей'))
        self.stdout.write('')
        self.stdout.write(self.style.SUCCESS('📋 Для входа в систему используйте:'))
        self.stdout.write('   • admin / admin123 (администратор)')
        self.stdout.write('   • testuser / test123 (обычный пользователь)')
        self.stdout.write('   • anna / anna123')
        self.stdout.write('   • mikhail / mikhail123')
        self.stdout.write('   • elena / elena123') 