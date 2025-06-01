import torch
import clip
from PIL import Image
import numpy as np
import faiss
from typing import List, Tuple, Union
import os
from advertisements.models import Advertisement
from django.conf import settings
import io

class CLIPService:
    def __init__(self):
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        self.model, self.preprocess = clip.load("ViT-B/32", device=self.device)
        self.index = None
        self.advertisements = []
        
    def encode_image(self, image_input: Union[str, bytes, Image.Image]) -> np.ndarray:
        """Кодирует изображение в вектор с помощью CLIP"""
        if isinstance(image_input, str):
            # Если передан путь к файлу
            image = Image.open(image_input)
        elif isinstance(image_input, bytes):
            # Если передан байтовый объект
            image = Image.open(io.BytesIO(image_input))
        elif isinstance(image_input, Image.Image):
            # Если передан объект PIL.Image
            image = image_input
        else:
            raise ValueError("Неподдерживаемый тип входных данных для изображения")
            
        image = self.preprocess(image).unsqueeze(0).to(self.device)
        with torch.no_grad():
            image_features = self.model.encode_image(image)
            image_features /= image_features.norm(dim=-1, keepdim=True)
        return image_features.cpu().numpy()
    
    def encode_text(self, text: str) -> np.ndarray:
        """Кодирует текст в вектор с помощью CLIP"""
        text_tokens = clip.tokenize([text]).to(self.device)
        with torch.no_grad():
            text_features = self.model.encode_text(text_tokens)
            text_features /= text_features.norm(dim=-1, keepdim=True)
        return text_features.cpu().numpy()
    
    def build_index(self):
        """Строит индекс FAISS для быстрого поиска"""
        # Получаем все объявления с фотографиями
        self.advertisements = Advertisement.objects.exclude(photo='')
        features = []
        
        for ad in self.advertisements:
            if ad.photo:
                feature = self.encode_image(ad.photo.path)
                features.append(feature)
            
        if features:
            features = np.vstack(features)
            self.index = faiss.IndexFlatIP(features.shape[1])
            self.index.add(features)
    
    def search(self, query: Union[str, bytes, Image.Image], top_k: int = 5) -> List[Tuple[Advertisement, float]]:
        """Поиск похожих животных по тексту или изображению"""
        if isinstance(query, str):
            if os.path.isfile(query):
                query_vector = self.encode_image(query)
            else:
                query_vector = self.encode_text(query)
        else:
            query_vector = self.encode_image(query)
            
        distances, indices = self.index.search(query_vector, top_k)
        
        results = []
        for idx, distance in zip(indices[0], distances[0]):
            if idx != -1:  # FAISS возвращает -1 для пустых результатов
                # Преобразуем numpy.int64 в обычный int
                idx = int(idx)
                results.append((self.advertisements[idx], float(distance)))
                
        return results 