import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import Dataset, DataLoader
import torchvision.transforms as transforms
from PIL import Image
import requests
import io
import numpy as np
import timm
import logging
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder
import json
import os

# Настройка логирования
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Конфигурация
DJANGO_API_URL = "http://localhost:8000/api"
MODEL_WEIGHTS_FILE = "pet_classifier.pth"
BATCH_SIZE = 16
EPOCHS = 20
LEARNING_RATE = 0.001

# Маппинг типов животных
ANIMAL_TYPES = ['cat', 'dog', 'bird', 'rodent', 'rabbit', 'reptile', 'other']

class PetDataset(Dataset):
    def __init__(self, data, transform=None):
        self.data = data
        self.transform = transform
        
    def __len__(self):
        return len(self.data)
    
    def __getitem__(self, idx):
        item = self.data[idx]
        
        # Загружаем изображение
        try:
            image_url = item['photo']
            if image_url.startswith('/media/'):
                image_url = f"http://localhost:8000{image_url}"
            
            response = requests.get(image_url, timeout=10)
            if response.status_code == 200:
                image = Image.open(io.BytesIO(response.content))
                if image.mode != 'RGB':
                    image = image.convert('RGB')
            else:
                # Создаем пустое изображение если не удалось загрузить
                image = Image.new('RGB', (224, 224), color='gray')
        except Exception as e:
            logger.warning(f"Failed to load image {item['photo']}: {e}")
            image = Image.new('RGB', (224, 224), color='gray')
        
        if self.transform:
            image = self.transform(image)
        
        # Получаем метку класса
        animal_type = item['type']
        if animal_type not in ANIMAL_TYPES:
            animal_type = 'other'
        
        label = ANIMAL_TYPES.index(animal_type)
        
        return image, label

def get_training_data():
    """Получает данные для обучения из Django API"""
    try:
        response = requests.get(f"{DJANGO_API_URL}/advertisements/")
        if response.status_code == 200:
            data = response.json()
            # Фильтруем объявления с фотографиями
            filtered_data = [ad for ad in data if ad.get('photo')]
            logger.info(f"Loaded {len(filtered_data)} advertisements with photos")
            return filtered_data
        else:
            logger.error(f"Error fetching data: {response.status_code}")
            return []
    except Exception as e:
        logger.error(f"Error connecting to Django API: {e}")
        return []

def create_model():
    """Создает модель для классификации"""
    # Загружаем предобученную модель
    base_model = timm.create_model('efficientnet_b4', pretrained=True)
    
    # Извлекатель признаков
    class FeatureExtractor(nn.Module):
        def __init__(self, base_model):
            super().__init__()
            self.features = nn.Sequential(*list(base_model.children())[:-1])
            self.pool = nn.AdaptiveAvgPool2d(1)
            
        def forward(self, x):
            x = self.features(x)
            x = self.pool(x)
            return x.view(x.size(0), -1)
    
    feature_extractor = FeatureExtractor(base_model)
    
    # Классификатор
    classifier = nn.Sequential(
        nn.Linear(1792, 512),  # EfficientNet-B4 feature size
        nn.ReLU(),
        nn.Dropout(0.3),
        nn.Linear(512, 256),
        nn.ReLU(),
        nn.Dropout(0.2),
        nn.Linear(256, len(ANIMAL_TYPES))
    )
    
    return feature_extractor, classifier

def train_model():
    """Обучает модель на данных из базы"""
    logger.info("Starting model training...")
    
    # Получаем данные
    data = get_training_data()
    if len(data) < 10:
        logger.error("Not enough training data. Need at least 10 samples.")
        return
    
    # Разделяем на train/val
    train_data, val_data = train_test_split(data, test_size=0.2, random_state=42)
    logger.info(f"Training samples: {len(train_data)}, Validation samples: {len(val_data)}")
    
    # Преобразования для обучения
    train_transform = transforms.Compose([
        transforms.Resize((380, 380)),
        transforms.RandomHorizontalFlip(0.5),
        transforms.RandomRotation(10),
        transforms.ColorJitter(brightness=0.2, contrast=0.2, saturation=0.2),
        transforms.ToTensor(),
        transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225])
    ])
    
    val_transform = transforms.Compose([
        transforms.Resize((380, 380)),
        transforms.ToTensor(),
        transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225])
    ])
    
    # Создаем датасеты
    train_dataset = PetDataset(train_data, train_transform)
    val_dataset = PetDataset(val_data, val_transform)
    
    train_loader = DataLoader(train_dataset, batch_size=BATCH_SIZE, shuffle=True)
    val_loader = DataLoader(val_dataset, batch_size=BATCH_SIZE, shuffle=False)
    
    # Создаем модель
    feature_extractor, classifier = create_model()
    
    # Замораживаем feature extractor
    for param in feature_extractor.parameters():
        param.requires_grad = False
    
    # Оптимизатор и функция потерь
    optimizer = optim.Adam(classifier.parameters(), lr=LEARNING_RATE)
    criterion = nn.CrossEntropyLoss()
    
    # Обучение
    best_val_acc = 0.0
    
    for epoch in range(EPOCHS):
        # Обучение
        classifier.train()
        train_loss = 0.0
        train_correct = 0
        train_total = 0
        
        for batch_idx, (images, labels) in enumerate(train_loader):
            optimizer.zero_grad()
            
            # Извлекаем признаки
            with torch.no_grad():
                features = feature_extractor(images)
            
            # Классифицируем
            outputs = classifier(features)
            loss = criterion(outputs, labels)
            
            loss.backward()
            optimizer.step()
            
            train_loss += loss.item()
            _, predicted = outputs.max(1)
            train_total += labels.size(0)
            train_correct += predicted.eq(labels).sum().item()
            
            if batch_idx % 10 == 0:
                logger.info(f'Epoch {epoch+1}/{EPOCHS}, Batch {batch_idx}, Loss: {loss.item():.4f}')
        
        train_acc = 100. * train_correct / train_total
        
        # Валидация
        classifier.eval()
        val_loss = 0.0
        val_correct = 0
        val_total = 0
        
        with torch.no_grad():
            for images, labels in val_loader:
                features = feature_extractor(images)
                outputs = classifier(features)
                loss = criterion(outputs, labels)
                
                val_loss += loss.item()
                _, predicted = outputs.max(1)
                val_total += labels.size(0)
                val_correct += predicted.eq(labels).sum().item()
        
        val_acc = 100. * val_correct / val_total
        
        logger.info(f'Epoch {epoch+1}/{EPOCHS}:')
        logger.info(f'  Train Loss: {train_loss/len(train_loader):.4f}, Train Acc: {train_acc:.2f}%')
        logger.info(f'  Val Loss: {val_loss/len(val_loader):.4f}, Val Acc: {val_acc:.2f}%')
        
        # Сохраняем лучшую модель
        if val_acc > best_val_acc:
            best_val_acc = val_acc
            torch.save({
                'classifier': classifier.state_dict(),
                'epoch': epoch,
                'val_acc': val_acc,
                'animal_types': ANIMAL_TYPES
            }, MODEL_WEIGHTS_FILE)
            logger.info(f'New best model saved with validation accuracy: {val_acc:.2f}%')
    
    logger.info(f"Training completed. Best validation accuracy: {best_val_acc:.2f}%")

if __name__ == "__main__":
    train_model() 