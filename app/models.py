from sqlalchemy import Column, Integer, String, Float, DateTime, Text, Boolean, ForeignKey, JSON
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base

class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True)
    name = Column(String)
    preferences = Column(JSON, default={})
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    routes = relationship("Route", back_populates="user")
    chat_messages = relationship("ChatMessage", back_populates="user")

class Route(Base):
    __tablename__ = "routes"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    origin = Column(String, index=True)
    destination = Column(String, index=True)
    route_data = Column(JSON)  # Complete route information
    preferences = Column(JSON)  # User preferences for this route
    score = Column(Float)  # Route score/rating
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    user = relationship("User", back_populates="routes")

class ChatMessage(Base):
    __tablename__ = "chat_messages"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    message = Column(Text)
    response = Column(Text)
    intent = Column(String)  # Extracted intent from message
    entities = Column(JSON)  # Extracted entities
    confidence = Column(Float, nullable=True)  # Confidence score
    read_at = Column(DateTime(timezone=True), nullable=True)  # When message was read
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    user = relationship("User", back_populates="chat_messages")

class City(Base):
    __tablename__ = "cities"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    country = Column(String, index=True)
    latitude = Column(Float)
    longitude = Column(Float)
    population = Column(Integer)
    timezone = Column(String)

class Attraction(Base):
    __tablename__ = "attractions"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    city_id = Column(Integer, ForeignKey("cities.id"))
    category = Column(String)  # hotel, restaurant, gas_station, tourist_spot
    latitude = Column(Float)
    longitude = Column(Float)
    rating = Column(Float)
    description = Column(Text)
    price_range = Column(String)  # budget, moderate, luxury

class RouteSegment(Base):
    __tablename__ = "route_segments"
    
    id = Column(Integer, primary_key=True, index=True)
    route_id = Column(Integer, ForeignKey("routes.id"))
    segment_order = Column(Integer)
    origin = Column(String)
    destination = Column(String)
    distance = Column(Float)
    duration = Column(Float)
    cost = Column(Float)
    transport_type = Column(String)  # car, train, bus, etc.
    stops = Column(JSON)  # List of stops along the way 