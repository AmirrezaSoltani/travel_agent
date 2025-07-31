from pydantic import BaseModel, EmailStr
from typing import Optional, List, Dict, Any
from datetime import datetime

# User schemas
class UserBase(BaseModel):
    email: EmailStr
    name: Optional[str] = None

class UserCreate(UserBase):
    pass

class User(UserBase):
    id: int
    preferences: Dict[str, Any] = {}
    created_at: datetime
    
    class Config:
        from_attributes = True

# Route schemas
class RouteRequest(BaseModel):
    origin: str
    destination: str
    preferences: Optional[Dict[str, Any]] = None
    budget: Optional[float] = None
    duration_days: Optional[int] = None
    transport_type: Optional[str] = "car"

class RouteResponse(BaseModel):
    id: int
    origin: str
    destination: str
    route_data: Dict[str, Any]
    score: float
    total_distance: float
    total_duration: float
    total_cost: float
    stops: List[Dict[str, Any]]
    
    class Config:
        from_attributes = True

# Chat schemas
class ChatMessageRequest(BaseModel):
    message: str
    user_id: Optional[int] = None
    lang: Optional[str] = "en"

class ChatMessageResponse(BaseModel):
    id: int
    message: str
    response: str
    intent: Optional[str] = None
    entities: Optional[Dict[str, Any]] = None
    confidence: Optional[float] = None
    suggestions: Optional[List[str]] = None
    route_info: Optional[Dict[str, Any]] = None
    quick_actions: Optional[List[Dict[str, Any]]] = None
    sentiment: Optional[str] = None
    conversation_flow: Optional[str] = None
    follow_up_questions: Optional[List[str]] = None
    created_at: datetime
    
    class Config:
        from_attributes = True

class ChatHistoryResponse(BaseModel):
    history: List[Dict[str, Any]]
    context_history: List[Dict[str, Any]]
    total_count: int

class ChatContextResponse(BaseModel):
    user_id: str
    current_language: str
    conversation_count: int
    user_preferences: Dict[str, Any]
    conversation_flow: str
    sentiment_score: float
    user_satisfaction: float
    last_interaction: datetime

class SentimentAnalysisResponse(BaseModel):
    overall_sentiment: float
    recent_messages: List[Dict[str, Any]]
    satisfaction_score: float

class FeedbackRequest(BaseModel):
    satisfaction: float
    message: Optional[str] = None

class ChatAnalyticsResponse(BaseModel):
    total_interactions: int
    average_response_time: float
    preferred_intents: Dict[str, int]
    sentiment_trend: List[Dict[str, Any]]
    conversation_flow_pattern: str
    user_engagement_score: float

# City and Attraction schemas
class CityBase(BaseModel):
    name: str
    country: str
    latitude: float
    longitude: float

class City(CityBase):
    id: int
    population: Optional[int] = None
    timezone: Optional[str] = None
    
    class Config:
        from_attributes = True

class AttractionBase(BaseModel):
    name: str
    category: str
    latitude: float
    longitude: float
    rating: Optional[float] = None
    description: Optional[str] = None
    price_range: Optional[str] = None

class Attraction(AttractionBase):
    id: int
    city_id: int
    
    class Config:
        from_attributes = True

# Recommendation schemas
class RecommendationRequest(BaseModel):
    origin: str
    destination: str
    preferences: Dict[str, float] = {
        "fastest": 0.3,
        "cheapest": 0.3,
        "scenic": 0.2,
        "quiet": 0.2
    }
    budget: Optional[float] = None
    duration_days: Optional[int] = None
    transport_type: str = "car"
    include_attractions: bool = True

class RecommendationResponse(BaseModel):
    routes: List[RouteResponse]
    summary: Dict[str, Any]
    alternatives: List[Dict[str, Any]] 