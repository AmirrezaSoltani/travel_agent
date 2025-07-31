import numpy as np
import pandas as pd
from typing import List, Dict, Any, Tuple
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.cluster import KMeans
import json
import os
from app.core.config import settings

class RouteRecommender:
    def __init__(self):
        self.cities_data = self._load_cities_data()
        self.attractions_data = self._load_attractions_data()
        self.routes_data = self._load_routes_data()
        self.vectorizer = TfidfVectorizer(max_features=1000, stop_words='english')
        
    def _load_cities_data(self) -> List[Dict]:
        """بارگذاری داده‌های شهرها"""
        try:
            with open(f"{settings.data_dir}/cities.json", 'r', encoding='utf-8') as f:
                return json.load(f)
        except FileNotFoundError:
            return self._get_default_cities()
    
    def _load_attractions_data(self) -> List[Dict]:
        """بارگذاری داده‌های جاذبه‌ها"""
        try:
            with open(f"{settings.data_dir}/attractions.json", 'r', encoding='utf-8') as f:
                return json.load(f)
        except FileNotFoundError:
            return self._get_default_attractions()
    
    def _load_routes_data(self) -> List[Dict]:
        """بارگذاری داده‌های مسیرها"""
        try:
            with open(f"{settings.data_dir}/routes.json", 'r', encoding='utf-8') as f:
                return json.load(f)
        except FileNotFoundError:
            return []
    
    def _get_default_cities(self) -> List[Dict]:
        """شهرهای پیش‌فرض"""
        return [
            {"name": "تهران", "country": "ایران", "lat": 35.6892, "lng": 51.3890},
            {"name": "اصفهان", "country": "ایران", "lat": 32.6546, "lng": 51.6680},
            {"name": "شیراز", "country": "ایران", "lat": 29.5916, "lng": 52.5836},
            {"name": "تبریز", "country": "ایران", "lat": 38.0962, "lng": 46.2738},
            {"name": "مشهد", "country": "ایران", "lat": 36.2605, "lng": 59.6168},
            {"name": "یزد", "country": "ایران", "lat": 31.8974, "lng": 54.3569},
            {"name": "کاشان", "country": "ایران", "lat": 33.9850, "lng": 51.4100},
            {"name": "قم", "country": "ایران", "lat": 34.6416, "lng": 50.8746},
            {"name": "کرج", "country": "ایران", "lat": 35.8400, "lng": 50.9391},
            {"name": "اهواز", "country": "ایران", "lat": 31.3183, "lng": 48.6706}
        ]
    
    def _get_default_attractions(self) -> List[Dict]:
        """جاذبه‌های پیش‌فرض"""
        return [
            {"name": "میدان امام", "city": "اصفهان", "category": "tourist_spot", "lat": 32.6577, "lng": 51.6775, "rating": 4.8},
            {"name": "تخت جمشید", "city": "شیراز", "category": "tourist_spot", "lat": 29.9354, "lng": 52.8916, "rating": 4.9},
            {"name": "مسجد نصیرالملک", "city": "شیراز", "category": "tourist_spot", "lat": 29.6083, "lng": 52.5432, "rating": 4.7},
            {"name": "باغ ارم", "city": "شیراز", "category": "tourist_spot", "lat": 29.6361, "lng": 52.5244, "rating": 4.6},
            {"name": "کاخ گلستان", "city": "تهران", "category": "tourist_spot", "lat": 35.6804, "lng": 51.4203, "rating": 4.5},
            {"name": "برج آزادی", "city": "تهران", "category": "tourist_spot", "lat": 35.6994, "lng": 51.3375, "rating": 4.4},
            {"name": "مسجد شیخ لطف‌الله", "city": "اصفهان", "category": "tourist_spot", "lat": 32.6577, "lng": 51.6775, "rating": 4.8},
            {"name": "پل خواجو", "city": "اصفهان", "category": "tourist_spot", "lat": 32.6311, "lng": 51.6775, "rating": 4.6},
            {"name": "باغ فین", "city": "کاشان", "category": "tourist_spot", "lat": 33.9850, "lng": 51.4100, "rating": 4.5},
            {"name": "خانه طباطبایی", "city": "کاشان", "category": "tourist_spot", "lat": 33.9850, "lng": 51.4100, "rating": 4.4}
        ]
    
    def calculate_distance(self, lat1: float, lng1: float, lat2: float, lng2: float) -> float:
        """محاسبه فاصله بین دو نقطه (کیلومتر)"""
        from math import radians, cos, sin, asin, sqrt
        
        lat1, lng1, lat2, lng2 = map(radians, [lat1, lng1, lat2, lng2])
        dlat = lat2 - lat1
        dlng = lng2 - lng1
        a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlng/2)**2
        c = 2 * asin(sqrt(a))
        return 6371 * c  # Earth radius in km
    
    def find_city_coordinates(self, city_name: str) -> Tuple[float, float]:
        """یافتن مختصات شهر"""
        for city in self.cities_data:
            if city["name"].lower() == city_name.lower():
                return city["lat"], city["lng"]
        return None, None
    
    def get_route_score(self, route: Dict, preferences: Dict[str, float]) -> float:
        """محاسبه امتیاز مسیر بر اساس ترجیحات"""
        score = 0.0
        
        # امتیاز بر اساس سرعت
        if "fastest" in preferences:
            distance = route.get("distance", 0)
            duration = route.get("duration", 0)
            speed_score = 1.0 / (1.0 + distance / 100)  # Normalize distance
            score += preferences["fastest"] * speed_score
        
        # امتیاز بر اساس هزینه
        if "cheapest" in preferences:
            cost = route.get("cost", 0)
            cost_score = 1.0 / (1.0 + cost / 1000)  # Normalize cost
            score += preferences["cheapest"] * cost_score
        
        # امتیاز بر اساس زیبایی
        if "scenic" in preferences:
            attractions = route.get("attractions", [])
            scenic_score = min(len(attractions) / 10.0, 1.0)  # Max 10 attractions
            score += preferences["scenic"] * scenic_score
        
        # امتیاز بر اساس آرامش
        if "quiet" in preferences:
            population = route.get("population", 0)
            quiet_score = 1.0 / (1.0 + population / 1000000)  # Normalize population
            score += preferences["quiet"] * quiet_score
        
        return score
    
    def recommend_routes(self, origin: str, destination: str, preferences: Dict[str, float], 
                        budget: float = None, duration_days: int = None) -> List[Dict]:
        """پیشنهاد مسیرهای سفر"""
        
        # یافتن مختصات مبدا و مقصد
        origin_lat, origin_lng = self.find_city_coordinates(origin)
        dest_lat, dest_lng = self.find_city_coordinates(destination)
        
        if not all([origin_lat, origin_lng, dest_lat, dest_lng]):
            return []
        
        # محاسبه فاصله مستقیم
        direct_distance = self.calculate_distance(origin_lat, origin_lng, dest_lat, dest_lng)
        
        # تولید مسیرهای مختلف
        routes = []
        
        # مسیر مستقیم
        direct_route = {
            "type": "direct",
            "distance": direct_distance,
            "duration": direct_distance / 80,  # فرض سرعت متوسط 80 کیلومتر بر ساعت
            "cost": direct_distance * 0.5,  # فرض هزینه 0.5 تومان به ازای هر کیلومتر
            "attractions": [],
            "population": 0,
            "segments": [{"origin": origin, "destination": destination}]
        }
        direct_route["score"] = self.get_route_score(direct_route, preferences)
        routes.append(direct_route)
        
        # مسیرهای با توقف
        intermediate_cities = self._find_intermediate_cities(origin_lat, origin_lng, dest_lat, dest_lng)
        
        for city in intermediate_cities[:3]:  # حداکثر 3 مسیر با توقف
            route = self._create_route_with_stops(origin, destination, city, preferences)
            if route:
                routes.append(route)
        
        # مرتب‌سازی بر اساس امتیاز
        routes.sort(key=lambda x: x["score"], reverse=True)
        
        # اعمال فیلترهای بودجه و زمان
        if budget:
            routes = [r for r in routes if r["cost"] <= budget]
        
        if duration_days:
            routes = [r for r in routes if r["duration"] <= duration_days * 24]
        
        return routes[:settings.max_routes_per_request]
    
    def _find_intermediate_cities(self, origin_lat: float, origin_lng: float, 
                                 dest_lat: float, dest_lng: float) -> List[Dict]:
        """یافتن شهرهای میانی مناسب"""
        intermediate_cities = []
        
        for city in self.cities_data:
            city_lat, city_lng = city["lat"], city["lng"]
            
            # محاسبه فاصله از مبدا و مقصد
            dist_from_origin = self.calculate_distance(origin_lat, origin_lng, city_lat, city_lng)
            dist_to_dest = self.calculate_distance(city_lat, city_lng, dest_lat, dest_lng)
            direct_dist = self.calculate_distance(origin_lat, origin_lng, dest_lat, dest_lng)
            
            # بررسی اینکه آیا شهر میانی منطقی است
            if dist_from_origin < direct_dist and dist_to_dest < direct_dist:
                # محاسبه امتیاز شهر میانی
                detour_ratio = (dist_from_origin + dist_to_dest) / direct_dist
                if detour_ratio < 1.5:  # حداکثر 50% انحراف
                    city["detour_ratio"] = detour_ratio
                    intermediate_cities.append(city)
        
        # مرتب‌سازی بر اساس نسبت انحراف
        intermediate_cities.sort(key=lambda x: x["detour_ratio"])
        return intermediate_cities
    
    def _create_route_with_stops(self, origin: str, destination: str, 
                                intermediate_city: Dict, preferences: Dict[str, float]) -> Dict:
        """ایجاد مسیر با توقف در شهر میانی"""
        
        # یافتن جاذبه‌های شهر میانی
        attractions = [a for a in self.attractions_data if a["city"] == intermediate_city["name"]]
        
        # محاسبه مسافت‌ها
        origin_lat, origin_lng = self.find_city_coordinates(origin)
        dest_lat, dest_lng = self.find_city_coordinates(destination)
        
        dist1 = self.calculate_distance(origin_lat, origin_lng, 
                                      intermediate_city["lat"], intermediate_city["lng"])
        dist2 = self.calculate_distance(intermediate_city["lat"], intermediate_city["lng"], 
                                      dest_lat, dest_lng)
        
        total_distance = dist1 + dist2
        total_duration = total_distance / 80 + len(attractions) * 2  # 2 ساعت برای هر جاذبه
        total_cost = total_distance * 0.5 + len(attractions) * 50  # 50 تومان برای هر جاذبه
        
        route = {
            "type": "with_stops",
            "distance": total_distance,
            "duration": total_duration,
            "cost": total_cost,
            "attractions": attractions,
            "population": intermediate_city.get("population", 0),
            "segments": [
                {"origin": origin, "destination": intermediate_city["name"]},
                {"origin": intermediate_city["name"], "destination": destination}
            ],
            "intermediate_city": intermediate_city["name"]
        }
        
        route["score"] = self.get_route_score(route, preferences)
        return route
    
    def get_attractions_near_route(self, route: Dict, max_distance: float = 50) -> List[Dict]:
        """یافتن جاذبه‌های نزدیک به مسیر"""
        nearby_attractions = []
        
        for attraction in self.attractions_data:
            # محاسبه فاصله از مسیر (ساده‌سازی)
            for segment in route["segments"]:
                origin_lat, origin_lng = self.find_city_coordinates(segment["origin"])
                dest_lat, dest_lng = self.find_city_coordinates(segment["destination"])
                
                if all([origin_lat, origin_lng, dest_lat, dest_lng]):
                    # محاسبه فاصله از خط مسیر
                    dist = self._distance_from_line(attraction["lat"], attraction["lng"],
                                                   origin_lat, origin_lng, dest_lat, dest_lng)
                    if dist <= max_distance:
                        attraction["distance_from_route"] = dist
                        nearby_attractions.append(attraction)
                        break
        
        return sorted(nearby_attractions, key=lambda x: x["distance_from_route"])
    
    def _distance_from_line(self, point_lat: float, point_lng: float,
                           line_lat1: float, line_lng1: float,
                           line_lat2: float, line_lng2: float) -> float:
        """محاسبه فاصله نقطه از خط (ساده‌سازی)"""
        # محاسبه فاصله از وسط خط
        mid_lat = (line_lat1 + line_lat2) / 2
        mid_lng = (line_lng1 + line_lng2) / 2
        return self.calculate_distance(point_lat, point_lng, mid_lat, mid_lng) 