import os
import requests
from pathlib import Path

def download_image(url, filename):
    response = requests.get(url)
    if response.status_code == 200:
        with open(filename, 'wb') as f:
            f.write(response.content)
        print(f"Downloaded {filename}")
    else:
        print(f"Failed to download {filename}")

def main():
    # Создаем директорию для тестовых изображений
    test_images_dir = Path(__file__).parent.parent / 'test_images'
    test_images_dir.mkdir(exist_ok=True)

    # Список тестовых изображений
    images = [
        {
            'url': 'https://images.unsplash.com/photo-1514888286974-6c03e2ca1dba',
            'filename': 'cat1.jpg'
        },
        {
            'url': 'https://images.unsplash.com/photo-1533738363-b7f9aef128ce',
            'filename': 'cat2.jpg'
        },
        {
            'url': 'https://images.unsplash.com/photo-1543466835-00a7907e9de1',
            'filename': 'dog1.jpg'
        },
        {
            'url': 'https://images.unsplash.com/photo-1552053831-71594a27632d',
            'filename': 'dog2.jpg'
        }
    ]

    # Скачиваем изображения
    for image in images:
        filepath = test_images_dir / image['filename']
        download_image(image['url'], filepath)

if __name__ == '__main__':
    main() 