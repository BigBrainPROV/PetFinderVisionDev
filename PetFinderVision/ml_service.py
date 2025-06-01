from fastapi import FastAPI, File, UploadFile
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
import torch
import clip
from PIL import Image
import io
import numpy as np
from typing import Dict, Any
import logging

# Настройка логирования
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI()

# Настройка CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Инициализация модели CLIP
device = "cuda" if torch.cuda.is_available() else "cpu"
model, preprocess = clip.load("ViT-B/32", device=device)

@app.get("/health")
async def health_check():
    return {"status": "ok"}

@app.post("/predict")
async def predict(file: UploadFile = File(...)) -> Dict[str, Any]:
    try:
        # Читаем содержимое файла
        contents = await file.read()
        image = Image.open(io.BytesIO(contents))
        
        # Предобработка изображения
        image_input = preprocess(image).unsqueeze(0).to(device)
        
        # Получаем эмбеддинги изображения
        with torch.no_grad():
            image_features = model.encode_image(image_input)
            image_features /= image_features.norm(dim=-1, keepdim=True)
        
        # Определяем тип животного
        animal_types = ["cat", "dog", "bird", "rodent", "rabbit", "reptile"]
        animal_texts = [f"a photo of a {animal}" for animal in animal_types]
        text_tokens = clip.tokenize(animal_texts).to(device)
        
        with torch.no_grad():
            text_features = model.encode_text(text_tokens)
            text_features /= text_features.norm(dim=-1, keepdim=True)
            
        # Вычисляем схожесть
        similarity = (100.0 * image_features @ text_features.T).softmax(dim=-1)
        values, indices = similarity[0].topk(1)
        
        animal_type = animal_types[indices[0].item()]
        confidence = values[0].item()
        
        # Определяем цвет
        colors = ["black", "white", "gray", "brown", "red", "orange", "yellow", "green", "blue", "purple"]
        color_texts = [f"a {color} animal" for color in colors]
        color_tokens = clip.tokenize(color_texts).to(device)
        
        with torch.no_grad():
            color_features = model.encode_text(color_tokens)
            color_features /= color_features.norm(dim=-1, keepdim=True)
            
        color_similarity = (100.0 * image_features @ color_features.T).softmax(dim=-1)
        color_values, color_indices = color_similarity[0].topk(1)
        
        color = colors[color_indices[0].item()]
        color_confidence = color_values[0].item()
        
        return {
            "animal_type": {
                "label": animal_type,
                "confidence": confidence
            },
            "color": {
                "label": color,
                "confidence": color_confidence
            }
        }
        
    except Exception as e:
        logger.error(f"Ошибка при обработке изображения: {str(e)}")
        raise

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=5001) 