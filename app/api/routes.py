from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional
import json

from app.database import get_db
from app.core.recommender import RouteRecommender
from app.services.map_service import MapService
from app.schemas import (
    RouteRequest, RouteResponse, RecommendationRequest, 
    RecommendationResponse, City, Attraction
)
from app.models import User, Route as RouteModel

router = APIRouter()
recommender = RouteRecommender()
map_service = MapService()

@router.post("/recommend", response_model=RecommendationResponse)
async def recommend_routes(request: RecommendationRequest):
    try:
        routes = recommender.recommend_routes(
            origin=request.origin,
            destination=request.destination,
            preferences=request.preferences,
            budget=request.budget,
            duration_days=request.duration_days
        )
        
        if not routes:
            raise HTTPException(status_code=404, detail="No suitable route found")
        
        route_responses = []
        for route in routes:
            route_response = RouteResponse(
                id=len(route_responses) + 1,
                origin=request.origin,
                destination=request.destination,
                route_data=route,
                score=route.get('score', 0.0),
                total_distance=route.get('distance', 0.0),
                total_duration=route.get('duration', 0.0),
                total_cost=route.get('cost', 0.0),
                stops=route.get('attractions', [])
            )
            route_responses.append(route_response)
        
        summary = {
            "total_routes": len(route_responses),
            "best_score": max(r.score for r in route_responses),
            "average_cost": sum(r.total_cost for r in route_responses) / len(route_responses),
            "average_duration": sum(r.total_duration for r in route_responses) / len(route_responses)
        }
        
        alternatives = []
        for route in routes[:3]:
            if route.get('intermediate_city'):
                alternatives.append({
                    "type": "intermediate_stop",
                    "city": route['intermediate_city'],
                    "description": f"Stop at {route['intermediate_city']} to visit attractions"
                })
        
        return RecommendationResponse(
            routes=route_responses,
            summary=summary,
            alternatives=alternatives
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Request processing error: {str(e)}")

@router.get("/cities", response_model=List[City])
async def get_cities(
    country: Optional[str] = Query(None, description="Filter by country"),
    search: Optional[str] = Query(None, description="Search in city names")
):
    try:
        cities = recommender.cities_data
        
        if country:
            cities = [city for city in cities if city.get('country', '').lower() == country.lower()]
        
        if search:
            cities = [city for city in cities if search.lower() in city.get('name', '').lower()]
        
        city_responses = []
        for city in cities:
            city_response = City(
                id=len(city_responses) + 1,
                name=city['name'],
                country=city['country'],
                latitude=city['lat'],
                longitude=city['lng'],
                population=city.get('population'),
                timezone=city.get('timezone')
            )
            city_responses.append(city_response)
        
        return city_responses
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching cities: {str(e)}")

@router.get("/attractions", response_model=List[Attraction])
async def get_attractions(
    city: Optional[str] = Query(None, description="Filter by city"),
    category: Optional[str] = Query(None, description="Filter by category"),
    min_rating: Optional[float] = Query(None, description="Minimum rating")
):
    try:
        attractions = recommender.attractions_data
        
        if city:
            attractions = [att for att in attractions if att.get('city', '').lower() == city.lower()]
        
        if category:
            attractions = [att for att in attractions if att.get('category', '').lower() == category.lower()]
        
        if min_rating:
            attractions = [att for att in attractions if att.get('rating', 0) >= min_rating]
        
        attraction_responses = []
        for attraction in attractions:
            attraction_response = Attraction(
                id=len(attraction_responses) + 1,
                name=attraction['name'],
                city_id=len(attraction_responses) + 1,  # Placeholder
                category=attraction['category'],
                latitude=attraction['lat'],
                longitude=attraction['lng'],
                rating=attraction.get('rating'),
                description=attraction.get('description'),
                price_range=attraction.get('price_range')
            )
            attraction_responses.append(attraction_response)
        
        return attraction_responses
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching attractions: {str(e)}")

@router.get("/route/{route_id}")
async def get_route_details(route_id: int):
    try:
        # This would typically fetch from database
        # For now, return sample data
        return {
            "id": route_id,
            "segments": [
                {"origin": "Tehran", "destination": "Isfahan", "distance": 450, "duration": 5.5},
                {"origin": "Isfahan", "destination": "Shiraz", "distance": 480, "duration": 6.0}
            ],
            "attractions": [
                {"name": "Imam Square", "city": "Isfahan", "rating": 4.8},
                {"name": "Jameh Mosque", "city": "Shiraz", "rating": 4.9}
            ],
            "total_distance": 930,
            "total_duration": 11.5,
            "total_cost": 465
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching route details: {str(e)}")

@router.get("/map/route")
async def get_route_map(
    origin: str = Query(..., description="Origin"),
    destination: str = Query(..., description="Destination"),
    include_attractions: bool = Query(True, description="Include attractions"),
    lang: str = Query("fa", description="Language")
):
    try:
        # Get city coordinates
        city_coords = {
            'Tehran': [35.6892, 51.3890],
            'Isfahan': [32.6546, 51.6680],
            'Shiraz': [29.5916, 52.5836],
            'Tabriz': [38.0962, 46.2738],
            'Mashhad': [36.2605, 59.6168],
            'Yazd': [31.8974, 54.3569],
            'Kashan': [33.9850, 51.4100],
            'Qom': [34.6416, 50.8746],
            'Kerman': [35.8400, 50.9391],
            'Ahvaz': [31.3183, 48.6706]
        }
        
        origin_coords = city_coords.get(origin)
        dest_coords = city_coords.get(destination)
        
        if not origin_coords or not dest_coords:
            raise HTTPException(status_code=404, detail="City coordinates not found")
        
        # Calculate route information
        distance = map_service.calculate_route_distance([origin_coords, dest_coords])
        duration = map_service.estimate_travel_time(distance, 'car')
        cost = distance * 500  # 500 tomans per km
        
        # Get attractions if requested
        attractions = []
        if include_attractions:
            attractions = map_service.get_attractions_for_route(origin, destination)
        
        # Create route response
        route_data = {
            "origin": {
                "name": origin,
                "coordinates": origin_coords
            },
            "destination": {
                "name": destination,
                "coordinates": dest_coords
            },
            "route": {
                "coordinates": [origin_coords, dest_coords],
                "distance": round(distance, 1),
                "duration": round(duration, 1),
                "cost": round(cost / 1000, 0)  # Convert to thousands
            },
            "attractions": attractions
        }
        
        return route_data
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error creating map: {str(e)}")

@router.get("/nearby-places")
async def get_nearby_places(
    lat: float = Query(..., description="Latitude"),
    lng: float = Query(..., description="Longitude"),
    radius: float = Query(5000, description="Search radius (meters)"),
    place_type: Optional[str] = Query(None, description="Place type")
):
    try:
        places = map_service.find_nearby_places(lat, lng, radius, place_type)
        return {"places": places}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error finding nearby places: {str(e)}")

@router.get("/city-info/{city_name}")
async def get_city_info(city_name: str):
    try:
        city_info = map_service.get_city_info(city_name)
        
        if not city_info:
            raise HTTPException(status_code=404, detail="City info not found")
        
        return city_info
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching city info: {str(e)}")

@router.post("/save-route")
async def save_route(route_request: RouteRequest, db: Session = Depends(get_db)):
    try:
        # Create route recommendation
        routes = recommender.recommend_routes(
            origin=route_request.origin,
            destination=route_request.destination,
            preferences=route_request.preferences or {},
            budget=route_request.budget,
            duration_days=route_request.duration_days
        )
        
        if not routes:
            raise HTTPException(status_code=404, detail="No suitable route found")
        
        # Save best route to database
        best_route = routes[0]
        db_route = RouteModel(
            origin=route_request.origin,
            destination=route_request.destination,
            route_data=best_route,
            preferences=route_request.preferences or {},
            score=best_route.get('score', 0.0)
        )
        
        db.add(db_route)
        db.commit()
        db.refresh(db_route)
        
        return {"message": "Route saved successfully", "route_id": db_route.id}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error saving route: {str(e)}")

@router.get("/user-routes/{user_id}")
async def get_user_routes(user_id: int, db: Session = Depends(get_db)):
    try:
        routes = db.query(RouteModel).filter(RouteModel.user_id == user_id).all()
        
        route_responses = []
        for route in routes:
            route_response = RouteResponse(
                id=route.id,
                origin=route.origin,
                destination=route.destination,
                route_data=route.route_data,
                score=route.score,
                total_distance=route.route_data.get('distance', 0.0),
                total_duration=route.route_data.get('duration', 0.0),
                total_cost=route.route_data.get('cost', 0.0),
                stops=route.route_data.get('attractions', [])
            )
            route_responses.append(route_response)
        
        return route_responses
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching user routes: {str(e)}") 