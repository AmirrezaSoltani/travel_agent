from pydantic_settings import BaseSettings
from typing import Optional
import os

class Settings(BaseSettings):
    database_url: str = "sqlite:///./travel_agent.db"
    
    secret_key: str = "your-secret-key-change-in-production"
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30
    
    api_v1_str: str = "/api"
    project_name: str = "AI Travel Recommender Agent"
    
    openstreetmap_url: str = "https://nominatim.openstreetmap.org"
    geocoding_api_key: Optional[str] = None
    
    spacy_model: str = "en_core_web_sm"
    
    data_dir: str = "data"
    static_dir: str = "app/static"
    templates_dir: str = "templates"
    
    max_chat_history: int = 50
    chat_timeout: int = 300
    
    max_routes_per_request: int = 5
    default_route_preferences: dict = {
        "fastest": 0.3,
        "cheapest": 0.3,
        "scenic": 0.2,
        "quiet": 0.2
    }
    
    class Config:
        env_file = ".env"

settings = Settings() 