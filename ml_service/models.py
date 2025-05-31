from typing import List, Optional
from pydantic import BaseModel
from datetime import datetime

class AnimalType(BaseModel):
    label: str
    confidence: float

class Breed(BaseModel):
    label: str
    confidence: float

class Feature(BaseModel):
    label: str
    confidence: float

class Color(BaseModel):
    label: str
    confidence: float
    pattern: str

class BodyProportions(BaseModel):
    aspect_ratio: float
    compactness: float
    size_category: str

class UniqueFeature(BaseModel):
    present: bool
    confidence: float

class UniqueFeatures(BaseModel):
    heterochromia: Optional[UniqueFeature] = None
    ear_fold: Optional[UniqueFeature] = None
    flat_face: Optional[UniqueFeature] = None
    short_tail: Optional[UniqueFeature] = None

    class Config:
        extra = "allow"  # Разрешаем дополнительные поля

class ImageAnalysis(BaseModel):
    animal_type: AnimalType
    breed: Breed
    color: Color
    features: List[Feature]
    confidence: float
    body_proportions: Optional[BodyProportions]
    unique_features: Optional[UniqueFeatures]

class Location(BaseModel):
    latitude: float
    longitude: float
    address: str

class Contact(BaseModel):
    name: str
    phone: str
    email: Optional[str]

class LostPetAd(BaseModel):
    id: str
    title: str
    description: str
    animal_type: str
    breed: str
    color: str
    pattern: str
    features: List[str]
    image_url: str
    lost_date: datetime
    lost_location: Location
    contact: Contact
    reward: Optional[float]
    status: str  # 'active', 'found', 'closed'
    created_at: datetime
    updated_at: datetime
    similarity: Optional[float]
    match_type: Optional[str] = None

class SimilarPet(BaseModel):
    id: str
    type: str
    breed: str
    color: str
    pattern: str
    features: List[str]
    image_url: Optional[str]
    similarity: float

class SearchResponse(BaseModel):
    analysis: ImageAnalysis
    similar_pets: List[SimilarPet]
    similar_lost_pets: List[LostPetAd] 