from django.core.management.base import BaseCommand
from news.models import News
from django.utils import timezone
from datetime import timedelta
import random

class Command(BaseCommand):
    help = 'Generates sample news entries'

    def handle(self, *args, **options):
        # Текущее время
        now = timezone.now()
        
        news_entries = [
            {
                'title': 'Запуск нового функционала поиска по фотографии',
                'description': 'Мы рады сообщить о запуске новой функции поиска потерянных питомцев по фотографии! '
                             'Теперь вы можете загрузить фото вашего питомца, и наша система найдет похожих животных '
                             'в базе данных. Это значительно упрощает процесс поиска и увеличивает шансы на успешное '
                             'воссоединение с вашим любимцем.',
                'created_at': now - timedelta(days=random.randint(1, 5))
            },
            {
                'title': 'Сотрудничество с местными приютами',
                'description': 'PetFinderVision начинает сотрудничество с сетью городских приютов для животных. '
                             'Теперь информация о найденных животных будет автоматически проверяться по базам приютов, '
                             'что поможет быстрее находить потерявшихся питомцев. Кроме того, мы будем размещать '
                             'информацию о животных из приютов, ищущих новый дом.',
                'created_at': now - timedelta(days=random.randint(6, 10))
            },
            {
                'title': 'Обновление мобильного приложения',
                'description': 'Вышло крупное обновление нашего мобильного приложения! Добавлены push-уведомления '
                             'о новых объявлениях в вашем районе, улучшен интерфейс карты и добавлена возможность '
                             'быстрой публикации объявлений. Приложение доступно для скачивания в App Store и '
                             'Google Play.',
                'created_at': now - timedelta(days=random.randint(11, 15))
            },
            {
                'title': 'Статистика: 1000 счастливых историй',
                'description': 'Мы достигли важной вехи - благодаря PetFinderVision уже 1000 потерявшихся животных '
                             'вернулись домой! Это стало возможным благодаря активному участию нашего сообщества, '
                             'современным технологиям поиска и неравнодушным волонтерам. Спасибо всем, кто помогает '
                             'в поиске и возвращении питомцев домой.',
                'created_at': now - timedelta(days=random.randint(16, 20))
            },
            {
                'title': 'Запуск образовательной программы',
                'description': 'Анонсируем запуск серии бесплатных вебинаров по ответственному содержанию домашних '
                             'животных. Темы включают: предотвращение побегов, правильная идентификация питомцев, '
                             'действия при потере животного и многое другое. Регистрация уже открыта на нашем сайте.',
                'created_at': now - timedelta(days=random.randint(21, 25))
            }
        ]

        # Удаляем существующие новости перед созданием новых
        News.objects.all().delete()

        for news_data in news_entries:
            News.objects.create(**news_data)
            self.stdout.write(
                self.style.SUCCESS(
                    f'Successfully created news: {news_data["title"]} '
                    f'(date: {news_data["created_at"].strftime("%d.%m.%Y")})'
                )
            )

        self.stdout.write(self.style.SUCCESS('Successfully generated all news entries')) 