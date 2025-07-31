import numpy as np
import pandas as pd
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass
from sklearn.ensemble import RandomForestRegressor
from sklearn.preprocessing import StandardScaler
from sklearn.metrics.pairwise import cosine_similarity
import json
import logging

logger = logging.getLogger(__name__)

@dataclass
class UserPreferences:
    budget_range: str
    travel_style: str
    accessibility_needs: List[str]
    cultural_interests: List[str]
    seasonal_preferences: List[str]
    group_size: int
    max_duration_days: int
    preferred_transport: List[str]

@dataclass
class RouteConstraints:
    origin_city_id: int
    destination_city_id: int
    max_budget: Optional[int]
    max_duration_hours: Optional[float]
    must_visit_cities: List[int]
    avoid_cities: List[int]
    seasonal_restrictions: List[str]

@dataclass
class RouteSegment:
    origin_city_id: int
    destination_city_id: int
    distance_km: float
    duration_hours: float
    cost_toman: int
    scenic_rating: float
    cultural_significance: float
    safety_rating: float
    road_type: str
    seasonal_factors: Dict[str, float]

class AdvancedRouteRecommender:
    def __init__(self, db_session):
        self.db = db_session
        self.ml_model = None
        self.scaler = StandardScaler()
        self.user_profiles = {}
        self.seasonal_factors = self._load_seasonal_data()
        self.cultural_weights = self._load_cultural_weights()
        
    def _load_seasonal_data(self) -> Dict[str, Dict[str, float]]:
        return {
            'spring': {
                'temperature_factor': 1.2,
                'tourism_factor': 1.3,
                'road_condition_factor': 1.1,
                'cost_factor': 1.1
            },
            'summer': {
                'temperature_factor': 0.8,
                'tourism_factor': 0.9,
                'road_condition_factor': 1.0,
                'cost_factor': 0.9
            },
            'fall': {
                'temperature_factor': 1.1,
                'tourism_factor': 1.2,
                'road_condition_factor': 1.0,
                'cost_factor': 1.0
            },
            'winter': {
                'temperature_factor': 0.7,
                'tourism_factor': 0.8,
                'road_condition_factor': 0.8,
                'cost_factor': 0.8
            }
        }
    
    def _load_cultural_weights(self) -> Dict[str, float]:
        return {
            'historical': 1.3,
            'religious': 1.2,
            'cultural': 1.1,
            'natural': 1.0,
            'modern': 0.9,
            'unesco_heritage': 1.5
        }
    
    def train_ml_model(self, training_data: List[Dict]) -> None:
        """Train the ML model for route scoring"""
        try:
            # Prepare training data
            X = []
            y = []
            
            for route_data in training_data:
                features = self._extract_route_features(route_data)
                X.append(features)
                y.append(route_data['user_rating'])
            
            X = np.array(X)
            y = np.array(y)
            
            # Scale features
            X_scaled = self.scaler.fit_transform(X)
            
            # Train Random Forest model
            self.ml_model = RandomForestRegressor(
                n_estimators=100,
                max_depth=10,
                random_state=42
            )
            self.ml_model.fit(X_scaled, y)
            
            logger.info("ML model trained successfully")
            
        except Exception as e:
            logger.error(f"Error training ML model: {e}")
            self.ml_model = None
    
    def _extract_route_features(self, route_data: Dict) -> List[float]:
        """Extract features for ML model"""
        return [
            route_data.get('distance_km', 0),
            route_data.get('duration_hours', 0),
            route_data.get('cost_toman', 0),
            route_data.get('scenic_rating', 0),
            route_data.get('cultural_significance', 0),
            route_data.get('safety_rating', 0),
            route_data.get('user_rating', 0),
            route_data.get('seasonal_factor', 1.0),
            route_data.get('accessibility_score', 1.0)
        ]
    
    def recommend_routes(
        self, 
        user_preferences: UserPreferences,
        constraints: RouteConstraints,
        num_recommendations: int = 5
    ) -> List[Dict[str, Any]]:
        """
        Generate personalized route recommendations
        """
        try:
            # Get all possible route segments
            route_segments = self._get_route_segments(constraints)
            
            # Generate route combinations
            route_combinations = self._generate_route_combinations(
                route_segments, constraints
            )
            
            # Score each route
            scored_routes = []
            for route in route_combinations:
                score = self._calculate_route_score(route, user_preferences)
                route['score'] = score
                scored_routes.append(route)
            
            # Sort by score and return top recommendations
            scored_routes.sort(key=lambda x: x['score'], reverse=True)
            
            return scored_routes[:num_recommendations]
            
        except Exception as e:
            logger.error(f"Error in route recommendation: {e}")
            return []
    
    def _get_route_segments(self, constraints: RouteConstraints) -> List[RouteSegment]:
        """Get relevant route segments from database"""
        try:
            # Query database for route segments
            query = """
                SELECT rs.*, 
                       c1.name_fa as origin_name_fa, c1.name_en as origin_name_en,
                       c2.name_fa as dest_name_fa, c2.name_en as dest_name_en,
                       c1.tourism_rating as origin_tourism,
                       c2.tourism_rating as dest_tourism
                FROM route_segments rs
                JOIN cities c1 ON rs.origin_city_id = c1.id
                JOIN cities c2 ON rs.destination_city_id = c2.id
                WHERE (rs.origin_city_id = :origin_id OR rs.destination_city_id = :dest_id)
                AND rs.origin_city_id NOT IN :avoid_cities
                AND rs.destination_city_id NOT IN :avoid_cities
            """
            
            result = self.db.execute(query, {
                'origin_id': constraints.origin_city_id,
                'dest_id': constraints.destination_city_id,
                'avoid_cities': constraints.avoid_cities or []
            })
            
            segments = []
            for row in result:
                segment = RouteSegment(
                    origin_city_id=row.origin_city_id,
                    destination_city_id=row.destination_city_id,
                    distance_km=row.distance_km,
                    duration_hours=row.duration_hours,
                    cost_toman=row.toll_cost + row.fuel_cost,
                    scenic_rating=row.scenic_rating,
                    cultural_significance=self._calculate_cultural_significance(row),
                    safety_rating=row.safety_rating,
                    road_type=row.road_type,
                    seasonal_factors=self._get_seasonal_factors(row)
                )
                segments.append(segment)
            
            return segments
            
        except Exception as e:
            logger.error(f"Error getting route segments: {e}")
            return []
    
    def _calculate_cultural_significance(self, route_data) -> float:
        """Calculate cultural significance of a route"""
        significance = 0.0
        
        # Check for UNESCO sites
        if route_data.get('unesco_heritage'):
            significance += self.cultural_weights['unesco_heritage']
        
        # Check for historical sites
        if route_data.get('historical_period'):
            significance += self.cultural_weights['historical']
        
        # Check for religious sites
        if route_data.get('religious_significance'):
            significance += self.cultural_weights['religious']
        
        return min(significance, 5.0)  # Cap at 5.0
    
    def _get_seasonal_factors(self, route_data) -> Dict[str, float]:
        """Get seasonal adjustment factors for a route"""
        current_season = self._get_current_season()
        return self.seasonal_factors.get(current_season, {
            'temperature_factor': 1.0,
            'tourism_factor': 1.0,
            'road_condition_factor': 1.0,
            'cost_factor': 1.0
        })
    
    def _get_current_season(self) -> str:
        """Get current season based on date"""
        import datetime
        month = datetime.datetime.now().month
        
        if month in [3, 4, 5]:
            return 'spring'
        elif month in [6, 7, 8]:
            return 'summer'
        elif month in [9, 10, 11]:
            return 'fall'
        else:
            return 'winter'
    
    def _generate_route_combinations(
        self, 
        segments: List[RouteSegment], 
        constraints: RouteConstraints
    ) -> List[Dict[str, Any]]:
        """Generate possible route combinations"""
        routes = []
        
        # Direct routes
        for segment in segments:
            if (segment.origin_city_id == constraints.origin_city_id and 
                segment.destination_city_id == constraints.destination_city_id):
                routes.append({
                    'type': 'direct',
                    'segments': [segment],
                    'total_distance': segment.distance_km,
                    'total_duration': segment.duration_hours,
                    'total_cost': segment.cost_toman,
                    'waypoints': []
                })
        
        # Routes with waypoints
        for segment1 in segments:
            for segment2 in segments:
                if (segment1.origin_city_id == constraints.origin_city_id and
                    segment1.destination_city_id == segment2.origin_city_id and
                    segment2.destination_city_id == constraints.destination_city_id):
                    
                    routes.append({
                        'type': 'with_waypoints',
                        'segments': [segment1, segment2],
                        'total_distance': segment1.distance_km + segment2.distance_km,
                        'total_duration': segment1.duration_hours + segment2.duration_hours,
                        'total_cost': segment1.cost_toman + segment2.cost_toman,
                        'waypoints': [segment1.destination_city_id]
                    })
        
        return routes
    
    def _calculate_route_score(
        self, 
        route: Dict[str, Any], 
        user_preferences: UserPreferences
    ) -> float:
        """Calculate personalized route score"""
        try:
            # Base score calculation
            base_score = 0.0
            
            # Distance optimization (prefer shorter routes)
            distance_score = max(0, 5.0 - (route['total_distance'] / 100))
            base_score += distance_score * 0.2
            
            # Duration optimization
            duration_score = max(0, 5.0 - (route['total_duration'] / 2))
            base_score += duration_score * 0.2
            
            # Cost optimization based on budget
            cost_score = self._calculate_cost_score(route['total_cost'], user_preferences.budget_range)
            base_score += cost_score * 0.25
            
            # Cultural significance
            cultural_score = self._calculate_cultural_score(route, user_preferences)
            base_score += cultural_score * 0.2
            
            # Scenic value
            scenic_score = self._calculate_scenic_score(route)
            base_score += scenic_score * 0.15
            
            # Apply seasonal adjustments
            seasonal_factor = self._get_seasonal_adjustment(route)
            base_score *= seasonal_factor
            
            # Apply user preference adjustments
            preference_factor = self._apply_user_preferences(route, user_preferences)
            base_score *= preference_factor
            
            # Use ML model if available
            if self.ml_model:
                ml_score = self._get_ml_score(route, user_preferences)
                base_score = (base_score * 0.7) + (ml_score * 0.3)
            
            return min(base_score, 5.0)  # Cap at 5.0
            
        except Exception as e:
            logger.error(f"Error calculating route score: {e}")
            return 0.0
    
    def _calculate_cost_score(self, cost: int, budget_range: str) -> float:
        """Calculate cost score based on budget range"""
        budget_limits = {
            'low': 200000,
            'medium': 500000,
            'high': 1000000,
            'luxury': 2000000
        }
        
        limit = budget_limits.get(budget_range, 500000)
        
        if cost <= limit * 0.5:
            return 5.0
        elif cost <= limit * 0.8:
            return 4.0
        elif cost <= limit:
            return 3.0
        elif cost <= limit * 1.5:
            return 2.0
        else:
            return 1.0
    
    def _calculate_cultural_score(self, route: Dict, user_preferences: UserPreferences) -> float:
        """Calculate cultural significance score"""
        score = 0.0
        
        for segment in route['segments']:
            # Base cultural significance
            score += segment.cultural_significance
            
            # Check if user has cultural interests
            if user_preferences.cultural_interests:
                # Add bonus for cultural interests
                score += 0.5
        
        return min(score / len(route['segments']), 5.0)
    
    def _calculate_scenic_score(self, route: Dict) -> float:
        """Calculate scenic value score"""
        total_scenic = sum(segment.scenic_rating for segment in route['segments'])
        return min(total_scenic / len(route['segments']), 5.0)
    
    def _get_seasonal_adjustment(self, route: Dict) -> float:
        """Get seasonal adjustment factor"""
        current_season = self._get_current_season()
        seasonal_factors = self.seasonal_factors.get(current_season, {})
        return seasonal_factors.get('tourism_factor', 1.0)
    
    def _apply_user_preferences(self, route: Dict, user_preferences: UserPreferences) -> float:
        """Apply user preference adjustments"""
        factor = 1.0
        
        # Travel style adjustments
        if user_preferences.travel_style == 'budget':
            if route['total_cost'] > 300000:
                factor *= 0.8
        elif user_preferences.travel_style == 'luxury':
            if route['total_cost'] < 500000:
                factor *= 0.9
        
        # Group size adjustments
        if user_preferences.group_size > 4:
            # Prefer routes with good accommodation options
            factor *= 1.1
        
        return factor
    
    def _get_ml_score(self, route: Dict, user_preferences: UserPreferences) -> float:
        """Get ML model prediction score"""
        try:
            if not self.ml_model:
                return 3.0
            
            # Prepare features for ML model
            features = [
                route['total_distance'],
                route['total_duration'],
                route['total_cost'],
                self._calculate_scenic_score(route),
                self._calculate_cultural_score(route, user_preferences),
                3.0,  # Default user rating
                1.0,  # Default seasonal factor
                1.0   # Default accessibility score
            ]
            
            # Scale features
            features_scaled = self.scaler.transform([features])
            
            # Get prediction
            prediction = self.ml_model.predict(features_scaled)[0]
            return max(0.0, min(5.0, prediction))
            
        except Exception as e:
            logger.error(f"Error getting ML score: {e}")
            return 3.0
    
    def get_attractions_near_route(self, route: Dict, radius_km: float = 50) -> List[Dict]:
        """Get attractions near the route"""
        try:
            # Get all cities in the route
            city_ids = [route['segments'][0].origin_city_id]
            for segment in route['segments']:
                city_ids.append(segment.destination_city_id)
            
            # Query attractions near these cities
            query = """
                SELECT a.*, c.name_fa as city_name_fa, c.name_en as city_name_en
                FROM attractions a
                JOIN cities c ON a.city_id = c.id
                WHERE a.city_id IN :city_ids
                ORDER BY a.rating DESC
                LIMIT 20
            """
            
            result = self.db.execute(query, {'city_ids': city_ids})
            
            attractions = []
            for row in result:
                attractions.append({
                    'id': row.id,
                    'name_fa': row.name_fa,
                    'name_en': row.name_en,
                    'category': row.category,
                    'rating': row.rating,
                    'city_name_fa': row.city_name_fa,
                    'city_name_en': row.city_name_en,
                    'unesco_heritage': row.unesco_heritage,
                    'cultural_significance': row.cultural_significance
                })
            
            return attractions
            
        except Exception as e:
            logger.error(f"Error getting attractions near route: {e}")
            return []
    
    def update_user_preferences(self, user_id: str, new_preferences: Dict) -> None:
        """Update user preferences for future recommendations"""
        try:
            self.user_profiles[user_id] = new_preferences
            logger.info(f"Updated preferences for user {user_id}")
        except Exception as e:
            logger.error(f"Error updating user preferences: {e}")
    
    def get_personalized_suggestions(self, user_id: str) -> List[Dict]:
        """Get personalized travel suggestions based on user history"""
        try:
            user_profile = self.user_profiles.get(user_id)
            if not user_profile:
                return []
            
            # Get user's travel history
            query = """
                SELECT DISTINCT city_id, COUNT(*) as visit_count
                FROM user_travel_history
                WHERE user_id = :user_id
                GROUP BY city_id
                ORDER BY visit_count DESC
                LIMIT 5
            """
            
            result = self.db.execute(query, {'user_id': user_id})
            
            suggestions = []
            for row in result:
                # Get city information
                city_query = """
                    SELECT c.*, p.name_fa as province_name_fa
                    FROM cities c
                    JOIN provinces p ON c.province_id = p.id
                    WHERE c.id = :city_id
                """
                
                city_result = self.db.execute(city_query, {'city_id': row.city_id})
                city = city_result.fetchone()
                
                if city:
                    suggestions.append({
                        'city_id': row.city_id,
                        'city_name_fa': city.name_fa,
                        'city_name_en': city.name_en,
                        'province_name_fa': city.province_name_fa,
                        'visit_count': row.visit_count,
                        'tourism_rating': city.tourism_rating,
                        'suggestion_type': 'frequent_visit'
                    })
            
            return suggestions
            
        except Exception as e:
            logger.error(f"Error getting personalized suggestions: {e}")
            return [] 