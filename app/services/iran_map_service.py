"""
Iran-Focused Map Service
Interactive mapping service for Iranian travel with cultural context
"""

import folium
import json
import requests
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass
import logging
from datetime import datetime

logger = logging.getLogger(__name__)

@dataclass
class MapPoint:
    """Map point with cultural information"""
    lat: float
    lng: float
    name_fa: str
    name_en: str
    category: str
    cultural_significance: float
    description_fa: str
    description_en: str
    photos: List[str]
    rating: float

@dataclass
class RouteInfo:
    """Route information for mapping"""
    origin: MapPoint
    destination: MapPoint
    waypoints: List[MapPoint]
    distance_km: float
    duration_hours: float
    route_type: str  # direct, with_waypoints, cultural_tour
    cultural_highlights: List[MapPoint]

class IranMapService:
    """
    Iran-focused map service with cultural context
    """
    
    def __init__(self):
        self.iran_center = [32.4279, 53.6880]  # Center of Iran
        self.osrm_base_url = "http://router.project-osrm.org/route/v1"
        self.overpass_base_url = "https://overpass-api.de/api/interpreter"
        
        # Iranian provinces boundaries (simplified)
        self.province_boundaries = self._load_province_boundaries()
        
        # Cultural zones
        self.cultural_zones = self._load_cultural_zones()
        
        # UNESCO sites in Iran
        self.unesco_sites = self._load_unesco_sites()
        
        # Historical routes
        self.historical_routes = self._load_historical_routes()
    
    def _load_province_boundaries(self) -> Dict[str, List[List[float]]]:
        """Load Iranian province boundaries"""
        return {
            'تهران': [[35.5, 50.5], [35.9, 51.5]],
            'اصفهان': [[32.0, 51.0], [33.5, 52.5]],
            'فارس': [[29.0, 52.0], [30.5, 53.5]],
            'آذربایجان شرقی': [[37.5, 45.5], [39.0, 47.0]],
            'خراسان رضوی': [[35.5, 58.0], [37.0, 60.0]],
            'یزد': [[31.0, 53.5], [32.5, 55.0]],
            'اصفهان': [[33.5, 51.0], [34.5, 52.0]],  # Kashan
            'قم': [[34.0, 50.5], [35.0, 51.5]],
            'البرز': [[35.5, 50.5], [36.0, 51.0]],
            'خوزستان': [[30.5, 48.0], [32.0, 49.5]]
        }
    
    def _load_cultural_zones(self) -> Dict[str, Dict[str, Any]]:
        """Load Iranian cultural zones"""
        return {
            'central_iran': {
                'name_fa': 'ایران مرکزی',
                'name_en': 'Central Iran',
                'cities': ['تهران', 'اصفهان', 'کاشان', 'قم'],
                'characteristics': ['historical', 'cultural', 'religious'],
                'color': 'red'
            },
            'southern_iran': {
                'name_fa': 'جنوب ایران',
                'name_en': 'Southern Iran',
                'cities': ['شیراز', 'یزد', 'اهواز'],
                'characteristics': ['historical', 'traditional', 'desert'],
                'color': 'orange'
            },
            'northern_iran': {
                'name_fa': 'شمال ایران',
                'name_en': 'Northern Iran',
                'cities': ['تبریز', 'مشهد'],
                'characteristics': ['religious', 'historical', 'mountainous'],
                'color': 'green'
            }
        }
    
    def _load_unesco_sites(self) -> List[Dict[str, Any]]:
        """Load UNESCO World Heritage Sites in Iran"""
        return [
            {
                'name_fa': 'تخت جمشید',
                'name_en': 'Persepolis',
                'lat': 29.9354,
                'lng': 52.8916,
                'category': 'cultural',
                'year_inscribed': 1979,
                'description_fa': 'پایتخت امپراتوری هخامنشی',
                'description_en': 'Capital of Achaemenid Empire'
            },
            {
                'name_fa': 'میدان امام',
                'name_en': 'Imam Square',
                'lat': 32.6577,
                'lng': 51.6775,
                'category': 'cultural',
                'year_inscribed': 1979,
                'description_fa': 'میدان تاریخی اصفهان',
                'description_en': 'Historical square of Isfahan'
            },
            {
                'name_fa': 'باغ ارم',
                'name_en': 'Eram Garden',
                'lat': 29.6361,
                'lng': 52.5247,
                'category': 'cultural',
                'year_inscribed': 2011,
                'description_fa': 'باغ تاریخی شیراز',
                'description_en': 'Historical garden of Shiraz'
            },
            {
                'name_fa': 'کاخ گلستان',
                'name_en': 'Golestan Palace',
                'lat': 35.6804,
                'lng': 51.4203,
                'category': 'cultural',
                'year_inscribed': 2013,
                'description_fa': 'کاخ سلطنتی قاجار',
                'description_en': 'Qajar royal palace'
            },
            {
                'name_fa': 'شوشتر',
                'name_en': 'Shushtar',
                'lat': 32.0456,
                'lng': 48.8567,
                'category': 'cultural',
                'year_inscribed': 2009,
                'description_fa': 'سیستم آبیاری تاریخی',
                'description_en': 'Historical hydraulic system'
            }
        ]
    
    def _load_historical_routes(self) -> List[Dict[str, Any]]:
        """Load historical trade and cultural routes"""
        return [
            {
                'name_fa': 'جاده ابریشم',
                'name_en': 'Silk Road',
                'route_type': 'trade',
                'significance': 'Major trade route connecting East and West',
                'points': [
                    {'lat': 35.6892, 'lng': 51.3890, 'name': 'تهران'},
                    {'lat': 32.6546, 'lng': 51.6680, 'name': 'اصفهان'},
                    {'lat': 29.5916, 'lng': 52.5836, 'name': 'شیراز'}
                ]
            },
            {
                'name_fa': 'مسیر زیارتی',
                'name_en': 'Pilgrimage Route',
                'route_type': 'religious',
                'significance': 'Route connecting major religious sites',
                'points': [
                    {'lat': 35.6892, 'lng': 51.3890, 'name': 'تهران'},
                    {'lat': 34.6416, 'lng': 50.8746, 'name': 'قم'},
                    {'lat': 36.2605, 'lng': 59.6168, 'name': 'مشهد'}
                ]
            }
        ]
    
    def create_iran_map(self, center: Optional[List[float]] = None, zoom: int = 6) -> folium.Map:
        """Create a base map centered on Iran"""
        if center is None:
            center = self.iran_center
        
        # Create map with Iranian tiles
        m = folium.Map(
            location=center,
            zoom_start=zoom,
            tiles='OpenStreetMap',
            prefer_canvas=True
        )
        
        # Add Iranian cultural overlay
        self._add_cultural_overlay(m)
        
        return m
    
    def _add_cultural_overlay(self, m: folium.Map):
        """Add cultural overlay to the map"""
        # Add UNESCO sites
        for site in self.unesco_sites:
            folium.Marker(
                location=[site['lat'], site['lng']],
                popup=f"<b>{site['name_en']}</b><br>{site['description_en']}<br>UNESCO {site['year_inscribed']}",
                icon=folium.Icon(color='red', icon='star', prefix='fa'),
                tooltip=f"UNESCO: {site['name_en']}"
            ).add_to(m)
        
        # Add cultural zones
        for zone_id, zone_data in self.cultural_zones.items():
            # Create a polygon for the zone (simplified)
            zone_coords = self._get_zone_coordinates(zone_id)
            if zone_coords:
                folium.Polygon(
                    locations=zone_coords,
                    popup=f"<b>{zone_data['name_en']}</b><br>Cultural Zone",
                    color=zone_data['color'],
                    fill=True,
                    fillOpacity=0.1,
                    weight=2
                ).add_to(m)
    
    def _get_zone_coordinates(self, zone_id: str) -> Optional[List[List[float]]]:
        """Get coordinates for cultural zones"""
        zone_coords = {
            'central_iran': [
                [35.0, 50.5], [35.0, 52.5],
                [33.0, 52.5], [33.0, 50.5]
            ],
            'southern_iran': [
                [30.0, 52.0], [30.0, 54.0],
                [28.0, 54.0], [28.0, 52.0]
            ],
            'northern_iran': [
                [37.0, 45.0], [37.0, 47.0],
                [35.0, 47.0], [35.0, 45.0]
            ]
        }
        return zone_coords.get(zone_id)
    
    def add_route_to_map(self, m: folium.Map, route_info: RouteInfo, lang: str = 'en') -> folium.Map:
        """Add a route to the map with cultural context"""
        
        # Add origin marker
        origin_icon = folium.Icon(color='green', icon='play', prefix='fa')
        origin_popup = self._create_point_popup(route_info.origin, lang)
        folium.Marker(
            location=[route_info.origin.lat, route_info.origin.lng],
            popup=origin_popup,
            icon=origin_icon,
            tooltip=f"Origin: {route_info.origin.name_en if lang == 'en' else route_info.origin.name_fa}"
        ).add_to(m)
        
        # Add destination marker
        dest_icon = folium.Icon(color='red', icon='flag-checkered', prefix='fa')
        dest_popup = self._create_point_popup(route_info.destination, lang)
        folium.Marker(
            location=[route_info.destination.lat, route_info.destination.lng],
            popup=dest_popup,
            icon=dest_icon,
            tooltip=f"Destination: {route_info.destination.name_en if lang == 'en' else route_info.destination.name_fa}"
        ).add_to(m)
        
        # Add waypoints
        for i, waypoint in enumerate(route_info.waypoints):
            waypoint_icon = folium.Icon(color='blue', icon='map-marker', prefix='fa')
            waypoint_popup = self._create_point_popup(waypoint, lang)
            folium.Marker(
                location=[waypoint.lat, waypoint.lng],
                popup=waypoint_popup,
                icon=waypoint_icon,
                tooltip=f"Waypoint {i+1}: {waypoint.name_en if lang == 'en' else waypoint.name_fa}"
            ).add_to(m)
        
        # Add route line
        route_coords = self._get_route_coordinates(route_info)
        if route_coords:
            folium.PolyLine(
                locations=route_coords,
                popup=f"Route: {route_info.distance_km:.0f} km, {route_info.duration_hours:.1f} hours",
                color='blue',
                weight=4,
                opacity=0.8
            ).add_to(m)
        
        # Add cultural highlights
        for highlight in route_info.cultural_highlights:
            highlight_icon = folium.Icon(color='purple', icon='star', prefix='fa')
            highlight_popup = self._create_point_popup(highlight, lang)
            folium.Marker(
                location=[highlight.lat, highlight.lng],
                popup=highlight_popup,
                icon=highlight_icon,
                tooltip=f"Cultural: {highlight.name_en if lang == 'en' else highlight.name_fa}"
            ).add_to(m)
        
        return m
    
    def _create_point_popup(self, point: MapPoint, lang: str) -> str:
        """Create HTML popup for a map point"""
        if lang == 'fa':
            return f"""
            <div style="width: 200px;">
                <h4>{point.name_fa}</h4>
                <p><strong>دسته‌بندی:</strong> {point.category}</p>
                <p><strong>امتیاز فرهنگی:</strong> {point.cultural_significance:.1f}/5.0</p>
                <p><strong>امتیاز کلی:</strong> {point.rating:.1f}/5.0</p>
                <p>{point.description_fa}</p>
            </div>
            """
        else:
            return f"""
            <div style="width: 200px;">
                <h4>{point.name_en}</h4>
                <p><strong>Category:</strong> {point.category}</p>
                <p><strong>Cultural Significance:</strong> {point.cultural_significance:.1f}/5.0</p>
                <p><strong>Rating:</strong> {point.rating:.1f}/5.0</p>
                <p>{point.description_en}</p>
            </div>
            """
    
    def _get_route_coordinates(self, route_info: RouteInfo) -> List[List[float]]:
        """Get coordinates for the route line"""
        coords = []
        
        # Add origin
        coords.append([route_info.origin.lat, route_info.origin.lng])
        
        # Add waypoints
        for waypoint in route_info.waypoints:
            coords.append([waypoint.lat, waypoint.lng])
        
        # Add destination
        coords.append([route_info.destination.lat, route_info.destination.lng])
        
        return coords
    
    def get_route_from_osrm(self, origin: List[float], destination: List[float], waypoints: Optional[List[List[float]]] = None) -> Dict[str, Any]:
        """Get route from OSRM API"""
        try:
            # Build coordinates string
            coords = f"{origin[1]},{origin[0]}"
            if waypoints:
                for wp in waypoints:
                    coords += f";{wp[1]},{wp[0]}"
            coords += f";{destination[1]},{destination[0]}"
            
            # Make request to OSRM
            url = f"{self.osrm_base_url}/driving/{coords}"
            params = {
                'overview': 'full',
                'geometries': 'geojson',
                'annotations': 'true'
            }
            
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            
            if data['code'] == 'Ok' and data['routes']:
                route = data['routes'][0]
                return {
                    'distance': route['distance'] / 1000,  # Convert to km
                    'duration': route['duration'] / 3600,  # Convert to hours
                    'geometry': route['geometry'],
                    'legs': route['legs']
                }
            
            return None
            
        except Exception as e:
            logger.error(f"Error getting route from OSRM: {e}")
            return None
    
    def find_nearby_places(self, lat: float, lng: float, radius: int = 5000, categories: Optional[List[str]] = None) -> List[Dict[str, Any]]:
        """Find nearby places using Overpass API"""
        try:
            # Build Overpass query
            if categories is None:
                categories = ['tourism', 'historic', 'religious', 'restaurant', 'hotel']
            
            query_parts = []
            for category in categories:
                query_parts.append(f'node["tourism"](around:{radius},{lat},{lng});')
                query_parts.append(f'node["historic"](around:{radius},{lat},{lng});')
                query_parts.append(f'node["amenity"="restaurant"](around:{radius},{lat},{lng});')
                query_parts.append(f'node["tourism"="hotel"](around:{radius},{lat},{lng});')
            
            query = f"""
            [out:json][timeout:25];
            (
                {''.join(query_parts)}
            );
            out body;
            >;
            out skel qt;
            """
            
            response = requests.post(self.overpass_base_url, data=query, timeout=30)
            response.raise_for_status()
            
            data = response.json()
            
            places = []
            for element in data.get('elements', []):
                if element['type'] == 'node':
                    place = {
                        'id': element['id'],
                        'lat': element['lat'],
                        'lng': element['lon'],
                        'tags': element.get('tags', {}),
                        'name': element.get('tags', {}).get('name', 'Unknown'),
                        'category': self._categorize_place(element.get('tags', {}))
                    }
                    places.append(place)
            
            return places
            
        except Exception as e:
            logger.error(f"Error finding nearby places: {e}")
            return []
    
    def _categorize_place(self, tags: Dict[str, str]) -> str:
        """Categorize a place based on its tags"""
        if 'historic' in tags:
            return 'historical'
        elif 'tourism' in tags:
            return 'tourist'
        elif 'amenity' in tags and tags['amenity'] == 'restaurant':
            return 'restaurant'
        elif 'tourism' in tags and tags['tourism'] == 'hotel':
            return 'hotel'
        elif 'religion' in tags:
            return 'religious'
        else:
            return 'other'
    
    def create_cultural_tour_map(self, cities: List[str], lang: str = 'en') -> folium.Map:
        """Create a map for a cultural tour"""
        # Create base map
        m = self.create_iran_map()
        
        # Add cultural tour route
        tour_points = []
        for city_name in cities:
            city_data = self._get_city_data(city_name)
            if city_data:
                tour_points.append(MapPoint(
                    lat=city_data['lat'],
                    lng=city_data['lng'],
                    name_fa=city_data['name_fa'],
                    name_en=city_data['name_en'],
                    category='cultural_tour',
                    cultural_significance=city_data['cultural_significance'],
                    description_fa=city_data['description_fa'],
                    description_en=city_data['description_en'],
                    photos=city_data.get('photos', []),
                    rating=city_data['rating']
                ))
        
        # Create route info
        if len(tour_points) >= 2:
            route_info = RouteInfo(
                origin=tour_points[0],
                destination=tour_points[-1],
                waypoints=tour_points[1:-1],
                distance_km=0,  # Will be calculated
                duration_hours=0,  # Will be calculated
                route_type='cultural_tour',
                cultural_highlights=tour_points
            )
            
            # Add route to map
            m = self.add_route_to_map(m, route_info, lang)
        
        return m
    
    def _get_city_data(self, city_name: str) -> Optional[Dict[str, Any]]:
        """Get city data by name"""
        city_database = {
            'تهران': {
                'lat': 35.6892, 'lng': 51.3890,
                'name_fa': 'تهران', 'name_en': 'Tehran',
                'cultural_significance': 4.2,
                'description_fa': 'پایتخت ایران و مرکز سیاسی و اقتصادی',
                'description_en': 'Capital of Iran and political/economic center',
                'rating': 4.2,
                'photos': []
            },
            'اصفهان': {
                'lat': 32.6546, 'lng': 51.6680,
                'name_fa': 'اصفهان', 'name_en': 'Isfahan',
                'cultural_significance': 4.8,
                'description_fa': 'شهر نصف جهان با معماری تاریخی باشکوه',
                'description_en': 'Half the World city with magnificent historical architecture',
                'rating': 4.8,
                'photos': []
            },
            'شیراز': {
                'lat': 29.5916, 'lng': 52.5836,
                'name_fa': 'شیراز', 'name_en': 'Shiraz',
                'cultural_significance': 4.7,
                'description_fa': 'شهر شعر و ادب و باغ‌های زیبا',
                'description_en': 'City of poetry and beautiful gardens',
                'rating': 4.7,
                'photos': []
            }
        }
        return city_database.get(city_name)
    
    def export_map_to_html(self, m: folium.Map, filename: str) -> str:
        """Export map to HTML file"""
        try:
            m.save(filename)
            return f"Map exported to {filename}"
        except Exception as e:
            logger.error(f"Error exporting map: {e}")
            return f"Error exporting map: {e}"
    
    def create_offline_map_data(self, region: str) -> Dict[str, Any]:
        """Create offline map data for a region"""
        offline_data = {
            'region': region,
            'timestamp': datetime.now().isoformat(),
            'cultural_sites': [],
            'routes': [],
            'cities': []
        }
        
        # Add cultural sites for the region
        if region == 'central_iran':
            offline_data['cultural_sites'] = [
                site for site in self.unesco_sites 
                if 32.0 <= site['lat'] <= 36.0 and 50.0 <= site['lng'] <= 53.0
            ]
        
        return offline_data 