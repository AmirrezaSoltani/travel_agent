import folium
import requests
import json
from typing import List, Dict, Tuple, Optional
from geopy.geocoders import Nominatim
from geopy.distance import geodesic
from app.core.config import settings

class MapService:
    def __init__(self):
        self.geolocator = Nominatim(user_agent="ai_travel_agent")
        self.base_url = settings.openstreetmap_url
        
    def geocode_city(self, city_name: str) -> Optional[Tuple[float, float]]:
        """تبدیل نام شهر به مختصات جغرافیایی"""
        try:
            location = self.geolocator.geocode(city_name)
            if location:
                return (location.latitude, location.longitude)
        except Exception as e:
            print(f"Error geocoding {city_name}: {e}")
        return None
    
    def reverse_geocode(self, lat: float, lng: float) -> Optional[str]:
        """تبدیل مختصات جغرافیایی به نام مکان"""
        try:
            location = self.geolocator.reverse(f"{lat}, {lng}")
            if location:
                return location.address
        except Exception as e:
            print(f"Error reverse geocoding {lat}, {lng}: {e}")
        return None
    
    def create_route_map(self, route: Dict, attractions: List[Dict] = None) -> str:
        """ایجاد نقشه مسیر با Folium"""
        
        # Find coordinates for route points
        route_coords = []
        for segment in route.get('segments', []):
            origin_coords = self.geocode_city(segment['origin'])
            dest_coords = self.geocode_city(segment['destination'])
            
            if origin_coords and dest_coords:
                route_coords.extend([origin_coords, dest_coords])
        
        if not route_coords:
            return None
        
        # Calculate center of map
        center_lat = sum(coord[0] for coord in route_coords) / len(route_coords)
        center_lng = sum(coord[1] for coord in route_coords) / len(route_coords)
        
        # Create map
        m = folium.Map(
            location=[center_lat, center_lng],
            zoom_start=8,
            tiles='OpenStreetMap'
        )
        
        # Add route line
        if len(route_coords) >= 2:
            folium.PolyLine(
                route_coords,
                weight=3,
                color='blue',
                opacity=0.8
            ).add_to(m)
        
        # Add markers for cities
        for i, coord in enumerate(route_coords):
            if i % 2 == 0:  # Origin cities
                folium.Marker(
                    coord,
                    popup=f"مبدا: {route['segments'][i//2]['origin']}",
                    icon=folium.Icon(color='green', icon='info-sign')
                ).add_to(m)
            else:  # Destination cities
                folium.Marker(
                    coord,
                    popup=f"مقصد: {route['segments'][i//2]['destination']}",
                    icon=folium.Icon(color='red', icon='info-sign')
                ).add_to(m)
        
        # Add attraction markers
        if attractions:
            for attraction in attractions:
                folium.Marker(
                    [attraction['lat'], attraction['lng']],
                    popup=f"{attraction['name']}<br>امتیاز: {attraction.get('rating', 'N/A')}",
                    icon=folium.Icon(color='orange', icon='star')
                ).add_to(m)
        
        # Save map to HTML string
        return m._repr_html_()
    
    def get_attractions_for_route(self, origin: str, destination: str) -> List[Dict]:
        """دریافت جاذبه‌های مسیر"""
        # Sample attractions data for major cities
        attractions_data = {
            'اصفهان': [
                {
                    'name': 'میدان امام',
                    'category': 'تاریخی',
                    'lat': 32.6577,
                    'lng': 51.6775,
                    'rating': 4.8,
                    'description': 'میدان تاریخی امام خمینی'
                },
                {
                    'name': 'مسجد شیخ لطف‌الله',
                    'category': 'مذهبی',
                    'lat': 32.6578,
                    'lng': 51.6776,
                    'rating': 4.7,
                    'description': 'مسجد تاریخی شیخ لطف‌الله'
                },
                {
                    'name': 'کاخ چهلستون',
                    'category': 'تاریخی',
                    'lat': 32.6580,
                    'lng': 51.6778,
                    'rating': 4.6,
                    'description': 'کاخ تاریخی چهلستون'
                }
            ],
            'شیراز': [
                {
                    'name': 'تخت جمشید',
                    'category': 'تاریخی',
                    'lat': 29.9354,
                    'lng': 52.8916,
                    'rating': 4.9,
                    'description': 'مجموعه تاریخی تخت جمشید'
                },
                {
                    'name': 'مسجد نصیرالملک',
                    'category': 'مذهبی',
                    'lat': 29.6083,
                    'lng': 52.5432,
                    'rating': 4.7,
                    'description': 'مسجد زیبای نصیرالملک'
                },
                {
                    'name': 'باغ ارم',
                    'category': 'طبیعی',
                    'lat': 29.6085,
                    'lng': 52.5435,
                    'rating': 4.5,
                    'description': 'باغ تاریخی ارم'
                }
            ],
            'تهران': [
                {
                    'name': 'برج آزادی',
                    'category': 'تاریخی',
                    'lat': 35.6994,
                    'lng': 51.3375,
                    'rating': 4.3,
                    'description': 'برج آزادی تهران'
                },
                {
                    'name': 'کاخ گلستان',
                    'category': 'تاریخی',
                    'lat': 35.6804,
                    'lng': 51.4203,
                    'rating': 4.4,
                    'description': 'کاخ تاریخی گلستان'
                },
                {
                    'name': 'موزه ملی ایران',
                    'category': 'فرهنگی',
                    'lat': 35.6892,
                    'lng': 51.3890,
                    'rating': 4.2,
                    'description': 'موزه ملی ایران'
                }
            ],
            'مشهد': [
                {
                    'name': 'حرم امام رضا',
                    'category': 'مذهبی',
                    'lat': 36.2605,
                    'lng': 59.6168,
                    'rating': 4.9,
                    'description': 'حرم مطهر امام رضا'
                },
                {
                    'name': 'گنبد سبز',
                    'category': 'تاریخی',
                    'lat': 36.2607,
                    'lng': 59.6170,
                    'rating': 4.1,
                    'description': 'گنبد سبز مشهد'
                }
            ],
            'یزد': [
                {
                    'name': 'مسجد جامع یزد',
                    'category': 'مذهبی',
                    'lat': 31.8974,
                    'lng': 54.3569,
                    'rating': 4.6,
                    'description': 'مسجد جامع تاریخی یزد'
                },
                {
                    'name': 'برج خاموشان',
                    'category': 'تاریخی',
                    'lat': 31.8976,
                    'lng': 54.3571,
                    'rating': 4.3,
                    'description': 'برج خاموشان یزد'
                }
            ],
            'کاشان': [
                {
                    'name': 'باغ فین',
                    'category': 'طبیعی',
                    'lat': 33.9850,
                    'lng': 51.4100,
                    'rating': 4.4,
                    'description': 'باغ تاریخی فین کاشان'
                },
                {
                    'name': 'خانه بروجردی‌ها',
                    'category': 'تاریخی',
                    'lat': 33.9852,
                    'lng': 51.4102,
                    'rating': 4.2,
                    'description': 'خانه تاریخی بروجردی‌ها'
                }
            ]
        }
        
        # Get attractions for both origin and destination
        route_attractions = []
        
        if origin in attractions_data:
            route_attractions.extend(attractions_data[origin])
        
        if destination in attractions_data:
            route_attractions.extend(attractions_data[destination])
        
        # Add some attractions along the route
        if origin == 'تهران' and destination == 'اصفهان':
            route_attractions.extend(attractions_data.get('کاشان', []))
        elif origin == 'اصفهان' and destination == 'شیراز':
            route_attractions.extend([
                {
                    'name': 'پاسارگاد',
                    'category': 'تاریخی',
                    'lat': 30.1956,
                    'lng': 53.1678,
                    'rating': 4.5,
                    'description': 'آرامگاه کوروش کبیر'
                }
            ])
        
        return route_attractions[:5]  # Return top 5 attractions
    
    def get_route_polyline(self, origin: str, destination: str) -> List[Tuple[float, float]]:
        """دریافت مسیر به صورت polyline از OpenStreetMap"""
        try:
            # Get coordinates
            origin_coords = self.geocode_city(origin)
            dest_coords = self.geocode_city(destination)
            
            if not origin_coords or not dest_coords:
                return []
            
            # Use OSRM for routing (if available)
            url = f"http://router.project-osrm.org/route/v1/driving/{origin_coords[1]},{origin_coords[0]};{dest_coords[1]},{dest_coords[0]}?overview=full&geometries=geojson"
            
            response = requests.get(url, timeout=10)
            if response.status_code == 200:
                data = response.json()
                if data['routes']:
                    coordinates = data['routes'][0]['geometry']['coordinates']
                    # Convert from [lng, lat] to [lat, lng]
                    return [(coord[1], coord[0]) for coord in coordinates]
            
            # Fallback to straight line
            return [origin_coords, dest_coords]
            
        except Exception as e:
            print(f"Error getting route polyline: {e}")
            return []
    
    def find_nearby_places(self, lat: float, lng: float, radius: float = 5000, 
                          place_type: str = None) -> List[Dict]:
        """یافتن مکان‌های نزدیک"""
        try:
            # Use Overpass API for OpenStreetMap data
            query = f"""
            [out:json][timeout:25];
            (
              node["amenity"](around:{radius},{lat},{lng});
              way["amenity"](around:{radius},{lat},{lng});
              relation["amenity"](around:{radius},{lat},{lng});
            );
            out body;
            >;
            out skel qt;
            """
            
            url = "https://overpass-api.de/api/interpreter"
            response = requests.post(url, data=query, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                places = []
                
                for element in data.get('elements', []):
                    if element['type'] == 'node' and 'tags' in element:
                        tags = element['tags']
                        if place_type is None or tags.get('amenity') == place_type:
                            places.append({
                                'name': tags.get('name', 'Unknown'),
                                'type': tags.get('amenity', 'unknown'),
                                'lat': element['lat'],
                                'lng': element['lon']
                            })
                
                return places
            
        except Exception as e:
            print(f"Error finding nearby places: {e}")
        
        return []
    
    def calculate_route_distance(self, route_coords: List[Tuple[float, float]]) -> float:
        """محاسبه فاصله کل مسیر"""
        total_distance = 0.0
        
        for i in range(len(route_coords) - 1):
            distance = geodesic(route_coords[i], route_coords[i + 1]).kilometers
            total_distance += distance
        
        return total_distance
    
    def estimate_travel_time(self, distance: float, transport_type: str = 'car') -> float:
        """تخمین زمان سفر"""
        speeds = {
            'car': 80,  # km/h
            'train': 120,
            'bus': 60,
            'bicycle': 20,
            'walking': 5
        }
        
        speed = speeds.get(transport_type, 80)
        return distance / speed  # hours
    
    def get_weather_info(self, lat: float, lng: float) -> Optional[Dict]:
        """دریافت اطلاعات آب و هوا (نمونه)"""
        # This would typically use a weather API
        # For now, return sample data
        return {
            'temperature': 25,
            'condition': 'sunny',
            'humidity': 60,
            'wind_speed': 10
        }
    
    def create_offline_map_data(self, bounds: Tuple[float, float, float, float], 
                               zoom_levels: List[int] = [10, 11, 12, 13]) -> Dict:
        """ایجاد داده‌های نقشه آفلاین"""
        # This would typically download map tiles
        # For now, return metadata
        return {
            'bounds': bounds,
            'zoom_levels': zoom_levels,
            'tile_count': len(zoom_levels) * 256,  # Approximate
            'size_mb': len(zoom_levels) * 50  # Approximate size
        }
    
    def get_city_info(self, city_name: str) -> Optional[Dict]:
        """دریافت اطلاعات شهر"""
        coords = self.geocode_city(city_name)
        if not coords:
            return None
        
        # Get additional info from OpenStreetMap
        try:
            query = f"""
            [out:json][timeout:25];
            area[name="{city_name}"][admin_level~"^[48]$"]->.searchArea;
            (
              node["place"="city"](area.searchArea);
              way["place"="city"](area.searchArea);
              relation["place"="city"](area.searchArea);
            );
            out body;
            >;
            out skel qt;
            """
            
            url = "https://overpass-api.de/api/interpreter"
            response = requests.post(url, data=query, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                if data.get('elements'):
                    element = data['elements'][0]
                    return {
                        'name': city_name,
                        'lat': coords[0],
                        'lng': coords[1],
                        'population': element.get('tags', {}).get('population'),
                        'timezone': element.get('tags', {}).get('timezone'),
                        'country': element.get('tags', {}).get('country')
                    }
        
        except Exception as e:
            print(f"Error getting city info: {e}")
        
        return {
            'name': city_name,
            'lat': coords[0],
            'lng': coords[1]
        }
    
    def validate_coordinates(self, lat: float, lng: float) -> bool:
        """اعتبارسنجی مختصات جغرافیایی"""
        return -90 <= lat <= 90 and -180 <= lng <= 180
    
    def format_distance(self, distance_km: float) -> str:
        """فرمت‌بندی فاصله"""
        if distance_km < 1:
            return f"{int(distance_km * 1000)} متر"
        elif distance_km < 1000:
            return f"{distance_km:.1f} کیلومتر"
        else:
            return f"{distance_km:.0f} کیلومتر"
    
    def format_duration(self, hours: float) -> str:
        """فرمت‌بندی مدت زمان"""
        if hours < 1:
            return f"{int(hours * 60)} دقیقه"
        elif hours < 24:
            return f"{hours:.1f} ساعت"
        else:
            days = hours / 24
            return f"{days:.1f} روز" 