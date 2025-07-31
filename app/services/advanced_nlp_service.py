import re
import json
import logging
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass
from datetime import datetime, timedelta
import spacy
from spacy.language import Language
from spacy.tokens import Doc, Span

logger = logging.getLogger(__name__)

@dataclass
class CulturalContext:
    season: str
    current_month: int
    religious_events: List[str]
    cultural_events: List[str]
    local_customs: List[str]
    accessibility_considerations: List[str]

@dataclass
class ExtractedIntent:
    primary_intent: str
    confidence: float
    cultural_context: CulturalContext
    seasonal_relevance: float
    cultural_significance: float

@dataclass
class IranianEntity:
    entity_type: str
    value: str
    persian_name: str
    english_name: str
    cultural_significance: float
    location_data: Dict[str, Any]

class AdvancedNLPService:
    def __init__(self):
        self.persian_pattern = re.compile(r'[\u0600-\u06FF\u0750-\u077F\u08A0-\u08FF\uFB50-\uFDFF\uFE70-\uFEFF]')
        self.english_pattern = re.compile(r'[a-zA-Z]')
        
        self.persian_to_english = self._load_persian_english_dict()
        self.english_to_persian = {v: k for k, v in self.persian_to_english.items()}
        
        self.iranian_cultural_terms = self._load_iranian_cultural_terms()
        self.intent_patterns = self._load_enhanced_intent_patterns()
        self.iranian_entities = self._load_iranian_entities()
        self.cultural_calendar = self._load_cultural_calendar()
        
        self.persian_nlp = None
        self.english_nlp = None
        self._initialize_spacy_models()
    
    def _load_persian_english_dict(self) -> Dict[str, str]:
        return {
            'مسیر': 'route',
            'سفر': 'travel',
            'از': 'from',
            'به': 'to',
            'بین': 'between',
            'بودجه': 'budget',
            'هزینه': 'cost',
            'زمان': 'time',
            'جاذبه': 'attraction',
            'ترجیح': 'preference',
            
            'میراث فرهنگی': 'cultural heritage',
            'مکان تاریخی': 'historical site',
            'مسجد': 'mosque',
            'کاخ': 'palace',
            'باغ': 'garden',
            'موزه': 'museum',
            'مقبره': 'tomb',
            'آرامگاه': 'mausoleum',
            'زیارتگاه': 'pilgrimage site',
            'حرم': 'shrine',
            
            'بهار': 'spring',
            'تابستان': 'summer',
            'پاییز': 'fall',
            'زمستان': 'winter',
            'نوروز': 'Nowruz',
            'محرم': 'Muharram',
            'رمضان': 'Ramadan',
            'عید': 'holiday',
            'جشن': 'celebration',
            'فستیوال': 'festival',
            
            'اتوبوس': 'bus',
            'قطار': 'train',
            'هواپیما': 'plane',
            'ماشین': 'car',
            'جاده': 'road',
            'اتوبان': 'highway',
            'فرودگاه': 'airport',
            'ایستگاه': 'station',
            
            'هتل': 'hotel',
            'مسافرخانه': 'guesthouse',
            'مهمانسرا': 'inn',
            'اقامتگاه': 'accommodation',
            'اتاق': 'room',
            'رزرو': 'reservation',
            
            'رستوران': 'restaurant',
            'کافه': 'cafe',
            'غذا': 'food',
            'کباب': 'kebab',
            'برنج': 'rice',
            'نان': 'bread',
            'چای': 'tea',
            'گلاب': 'rosewater',
            
            'زیارت': 'pilgrimage',
            'گردشگری': 'tourism',
            'بازدید': 'visit',
            'عکاسی': 'photography',
            'خرید': 'shopping',
            'بازار': 'bazaar',
            'صنایع دستی': 'handicrafts',
            
            'دسترسی': 'accessibility',
            'ویلچر': 'wheelchair',
            'آسانسور': 'elevator',
            'رامپ': 'ramp',
            'معلولیت': 'disability',
            
            'سریع': 'fast',
            'ارزان': 'cheap',
            'گران': 'expensive',
            'زیبا': 'beautiful',
            'آرام': 'quiet',
            'شلوغ': 'crowded',
            'مدرن': 'modern',
            'سنتی': 'traditional',
            'لوکس': 'luxury',
            'اقتصادی': 'economical'
        }
    
    def _load_iranian_cultural_terms(self) -> Dict[str, Dict[str, Any]]:
        return {
            'نوروز': {
                'english': 'Nowruz',
                'significance': 'Persian New Year',
                'season': 'spring',
                'cultural_importance': 5.0,
                'events': ['Haft-sin', 'Sizdah Bedar', 'Chaharshanbe Suri']
            },
            'تخت جمشید': {
                'english': 'Persepolis',
                'significance': 'Achaemenid capital',
                'category': 'historical',
                'unesco': True,
                'cultural_importance': 5.0
            },
            'میدان امام': {
                'english': 'Imam Square',
                'significance': 'UNESCO World Heritage Site',
                'category': 'historical',
                'unesco': True,
                'cultural_importance': 4.8
            },
            'حرم امام رضا': {
                'english': 'Imam Reza Shrine',
                'significance': 'Major pilgrimage site',
                'category': 'religious',
                'cultural_importance': 4.9
            },
            'باغ ارم': {
                'english': 'Eram Garden',
                'significance': 'Persian garden',
                'category': 'natural',
                'unesco': True,
                'cultural_importance': 4.5
            }
        }
    
    def _load_enhanced_intent_patterns(self) -> Dict[str, List[str]]:
        return {
            'route_request': [
                r'مسیر.*(?:از|به|بین).*',
                r'راه.*(?:از|به|بین).*',
                r'سفر.*(?:از|به|بین).*',
                r'برو.*(?:از|به|بین).*',
                r'چطور.*(?:برم|برسیم).*',
                r'مسیر.*(?:پیشنهاد|پیدا).*',
                r'route.*(?:from|to|between).*',
                r'way.*(?:from|to|between).*',
                r'travel.*(?:from|to|between).*',
                r'go.*(?:from|to|between).*',
                r'how.*(?:to|from|get).*',
                r'path.*(?:from|to|between).*'
            ],
            'cultural_heritage_request': [
                r'میراث.*فرهنگی.*',
                r'مکان.*تاریخی.*',
                r'بنا.*تاریخی.*',
                r'کاخ.*',
                r'مسجد.*',
                r'موزه.*',
                r'cultural.*heritage.*',
                r'historical.*site.*',
                r'palace.*',
                r'mosque.*',
                r'museum.*',
                r'ancient.*site.*'
            ],
            'religious_pilgrimage_request': [
                r'زیارت.*',
                r'حرم.*',
                r'مقبره.*',
                r'آرامگاه.*',
                r'مذهبی.*',
                r'pilgrimage.*',
                r'shrine.*',
                r'tomb.*',
                r'religious.*',
                r'sacred.*site.*'
            ],
            'seasonal_planning_request': [
                r'بهار.*',
                r'تابستان.*',
                r'پاییز.*',
                r'زمستان.*',
                r'نوروز.*',
                r'فصل.*',
                r'spring.*',
                r'summer.*',
                r'fall.*',
                r'winter.*',
                r'season.*',
                r'Nowruz.*'
            ],
            'budget_request': [
                r'بودجه.*',
                r'هزینه.*',
                r'قیمت.*',
                r'ارزان.*',
                r'گران.*',
                r'اقتصادی.*',
                r'budget.*',
                r'cost.*',
                r'price.*',
                r'cheap.*',
                r'expensive.*',
                r'economical.*'
            ],
            'accessibility_request': [
                r'دسترسی.*',
                r'ویلچر.*',
                r'آسانسور.*',
                r'معلولیت.*',
                r'رامپ.*',
                r'accessibility.*',
                r'wheelchair.*',
                r'elevator.*',
                r'disability.*',
                r'ramp.*'
            ],
            'food_culture_request': [
                r'غذا.*',
                r'رستوران.*',
                r'کباب.*',
                r'برنج.*',
                r'چای.*',
                r'گلاب.*',
                r'food.*',
                r'restaurant.*',
                r'kebab.*',
                r'rice.*',
                r'tea.*',
                r'rosewater.*'
            ]
        }
    
    def _load_iranian_entities(self) -> Dict[str, Dict[str, Any]]:
        return {
            'cities': {
                'تهران': {'en': 'Tehran', 'province': 'تهران', 'significance': 'capital'},
                'اصفهان': {'en': 'Isfahan', 'province': 'اصفهان', 'significance': 'cultural'},
                'شیراز': {'en': 'Shiraz', 'province': 'فارس', 'significance': 'poetry'},
                'تبریز': {'en': 'Tabriz', 'province': 'آذربایجان شرقی', 'significance': 'historical'},
                'مشهد': {'en': 'Mashhad', 'province': 'خراسان رضوی', 'significance': 'religious'},
                'یزد': {'en': 'Yazd', 'province': 'یزد', 'significance': 'traditional'},
                'کاشان': {'en': 'Kashan', 'province': 'اصفهان', 'significance': 'garden'},
                'قم': {'en': 'Qom', 'province': 'قم', 'significance': 'religious'},
                'کرج': {'en': 'Karaj', 'province': 'البرز', 'significance': 'industrial'},
                'اهواز': {'en': 'Ahvaz', 'province': 'خوزستان', 'significance': 'oil'}
            },
            'attractions': {
                'تخت جمشید': {'en': 'Persepolis', 'city': 'شیراز', 'category': 'historical'},
                'میدان امام': {'en': 'Imam Square', 'city': 'اصفهان', 'category': 'historical'},
                'حرم امام رضا': {'en': 'Imam Reza Shrine', 'city': 'مشهد', 'category': 'religious'},
                'باغ ارم': {'en': 'Eram Garden', 'city': 'شیراز', 'category': 'natural'},
                'کاخ گلستان': {'en': 'Golestan Palace', 'city': 'تهران', 'category': 'historical'},
                'مسجد نصیرالملک': {'en': 'Nasir al-Mulk Mosque', 'city': 'شیراز', 'category': 'religious'},
                'برج آزادی': {'en': 'Azadi Tower', 'city': 'تهران', 'category': 'modern'},
                'پل خواجو': {'en': 'Khaju Bridge', 'city': 'اصفهان', 'category': 'historical'},
                'خانه بروجردی‌ها': {'en': 'Borujerdi House', 'city': 'کاشان', 'category': 'historical'},
                'مسجد جامع یزد': {'en': 'Jameh Mosque of Yazd', 'city': 'یزد', 'category': 'religious'}
            }
        }
    
    def _load_cultural_calendar(self) -> Dict[str, List[Dict[str, Any]]]:
        return {
            'spring': [
                {'name_fa': 'نوروز', 'name_en': 'Nowruz', 'date': 'March 20-21', 'type': 'national'},
                {'name_fa': 'سیزده بدر', 'name_en': 'Sizdah Bedar', 'date': 'April 2', 'type': 'cultural'},
                {'name_fa': 'جشن گلاب‌گیری', 'name_en': 'Rosewater Festival', 'date': 'May', 'type': 'cultural'}
            ],
            'summer': [
                {'name_fa': 'جشنواره شعر شیراز', 'name_en': 'Shiraz Poetry Festival', 'date': 'September', 'type': 'cultural'}
            ],
            'fall': [
                {'name_fa': 'محرم', 'name_en': 'Muharram', 'date': 'Variable', 'type': 'religious'},
                {'name_fa': 'عاشورا', 'name_en': 'Ashura', 'date': 'Variable', 'type': 'religious'}
            ],
            'winter': [
                {'name_fa': 'یلدا', 'name_en': 'Yalda Night', 'date': 'December 21', 'type': 'cultural'},
                {'name_fa': 'جشنواره بادگیر', 'name_en': 'Wind Tower Festival', 'date': 'June', 'type': 'cultural'}
            ]
        }
    
    def _initialize_spacy_models(self):
        try:
            self.persian_nlp = spacy.load("xx_ent_wiki_sm")
            logger.info("Persian spaCy model loaded successfully")
        except OSError:
            logger.warning("Persian spaCy model not available. Install with: python -m spacy download xx_ent_wiki_sm")
            self.persian_nlp = None
        
        try:
            self.english_nlp = spacy.load("en_core_web_sm")
            logger.info("English spaCy model loaded successfully")
        except OSError:
            logger.warning("English spaCy model not available. Install with: python -m spacy download en_core_web_sm")
            self.english_nlp = None
    
    def detect_language(self, text: str) -> str:
        persian_chars = len(self.persian_pattern.findall(text))
        english_chars = len(self.english_pattern.findall(text))
        
        iranian_terms = sum(1 for term in self.iranian_cultural_terms.keys() if term in text)
        
        if persian_chars > english_chars or iranian_terms > 0:
            return 'fa'
        elif english_chars > persian_chars:
            return 'en'
        else:
            return 'mixed'
    
    def extract_enhanced_intent(self, text: str, lang: str = 'auto') -> ExtractedIntent:
        if lang == 'auto':
            lang = self.detect_language(text)
        
        cultural_context = self._get_cultural_context()
        
        primary_intent = 'unknown'
        confidence = 0.0
        
        for intent, patterns in self.intent_patterns.items():
            for pattern in patterns:
                if re.search(pattern, text, re.IGNORECASE):
                    primary_intent = intent
                    confidence = 0.8
                    break
            if primary_intent != 'unknown':
                break
        
        cultural_relevance = self._calculate_cultural_relevance(text, cultural_context)
        seasonal_relevance = self._calculate_seasonal_relevance(text, cultural_context)
        cultural_significance = self._calculate_cultural_significance(text)
        
        return ExtractedIntent(
            primary_intent=primary_intent,
            confidence=confidence,
            cultural_context=cultural_context,
            seasonal_relevance=seasonal_relevance,
            cultural_significance=cultural_significance
        )
    
    def extract_iranian_entities(self, text: str, lang: str) -> List[IranianEntity]:
        entities = []
        
        for city_fa, city_data in self.iranian_entities['cities'].items():
            if city_fa in text or city_data['en'] in text:
                entities.append(IranianEntity(
                    entity_type='city',
                    value=city_data['en'],
                    persian_name=city_fa,
                    english_name=city_data['en'],
                    cultural_significance=self._get_city_significance(city_fa),
                    location_data={'province': city_data['province'], 'significance': city_data['significance']}
                ))
        
        for attr_fa, attr_data in self.iranian_entities['attractions'].items():
            if attr_fa in text or attr_data['en'] in text:
                entities.append(IranianEntity(
                    entity_type='attraction',
                    value=attr_data['en'],
                    persian_name=attr_fa,
                    english_name=attr_data['en'],
                    cultural_significance=self._get_attraction_significance(attr_fa),
                    location_data={'city': attr_data['city'], 'category': attr_data['category']}
                ))
        
        for term_fa, term_data in self.iranian_cultural_terms.items():
            if term_fa in text or term_data['english'] in text:
                entities.append(IranianEntity(
                    entity_type='cultural_term',
                    value=term_data['english'],
                    persian_name=term_fa,
                    english_name=term_data['english'],
                    cultural_significance=term_data.get('cultural_importance', 3.0),
                    location_data=term_data
                ))
        
        return entities
    
    def _get_cultural_context(self) -> CulturalContext:
        now = datetime.now()
        current_month = now.month
        
        if current_month in [3, 4, 5]:
            season = 'spring'
        elif current_month in [6, 7, 8]:
            season = 'summer'
        elif current_month in [9, 10, 11]:
            season = 'fall'
        else:
            season = 'winter'
        
        current_events = self.cultural_calendar.get(season, [])
        
        return CulturalContext(
            season=season,
            current_month=current_month,
            religious_events=[e for e in current_events if e['type'] == 'religious'],
            cultural_events=[e for e in current_events if e['type'] == 'cultural'],
            local_customs=self._get_local_customs(season),
            accessibility_considerations=self._get_accessibility_considerations()
        )
    
    def _get_local_customs(self, season: str) -> List[str]:
        customs = {
            'spring': ['نوروز celebrations', 'Haft-sin table', 'Sizdah Bedar picnic'],
            'summer': ['Evening gatherings', 'Tea ceremonies', 'Garden visits'],
            'fall': ['Religious observances', 'Traditional cooking', 'Family gatherings'],
            'winter': ['Yalda celebrations', 'Indoor activities', 'Traditional foods']
        }
        return customs.get(season, [])
    
    def _get_accessibility_considerations(self) -> List[str]:
        return [
            'Wheelchair accessibility in historical sites',
            'Elevator availability in hotels',
            'Ramp access in public places',
            'Sign language interpretation',
            'Audio descriptions for visually impaired'
        ]
    
    def _calculate_cultural_relevance(self, text: str, context: CulturalContext) -> float:
        relevance = 0.0
        
        for term in self.iranian_cultural_terms.keys():
            if term in text:
                relevance += 0.3
        
        if context.season in text:
            relevance += 0.2
        
        for event in context.cultural_events + context.religious_events:
            if event['name_fa'] in text or event['name_en'] in text:
                relevance += 0.4
        
        return min(relevance, 1.0)
    
    def _calculate_seasonal_relevance(self, text: str, context: CulturalContext) -> float:
        seasonal_terms = {
            'spring': ['بهار', 'spring', 'نوروز', 'Nowruz'],
            'summer': ['تابستان', 'summer'],
            'fall': ['پاییز', 'fall', 'autumn'],
            'winter': ['زمستان', 'winter', 'یلدا', 'Yalda']
        }
        
        current_season_terms = seasonal_terms.get(context.season, [])
        
        for term in current_season_terms:
            if term in text:
                return 1.0
        
        return 0.0
    
    def _calculate_cultural_significance(self, text: str) -> float:
        significance = 0.0
        
        unesco_terms = ['تخت جمشید', 'میدان امام', 'باغ ارم', 'Persepolis', 'Imam Square', 'Eram Garden']
        for term in unesco_terms:
            if term in text:
                significance += 0.5
        
        religious_terms = ['حرم', 'مسجد', 'زیارت', 'shrine', 'mosque', 'pilgrimage']
        for term in religious_terms:
            if term in text:
                significance += 0.3
        
        historical_terms = ['تاریخی', 'کاخ', 'موزه', 'historical', 'palace', 'museum']
        for term in historical_terms:
            if term in text:
                significance += 0.2
        
        return min(significance, 1.0)
    
    def _get_city_significance(self, city_name: str) -> float:
        significance_map = {
            'اصفهان': 4.8,
            'شیراز': 4.7,
            'مشهد': 4.9,
            'تهران': 4.2,
            'یزد': 4.4,
            'کاشان': 4.6,
            'تبریز': 4.3,
            'قم': 4.1,
            'کرج': 3.8,
            'اهواز': 3.9
        }
        return significance_map.get(city_name, 3.0)
    
    def _get_attraction_significance(self, attraction_name: str) -> float:
        significance_map = {
            'تخت جمشید': 5.0,
            'میدان امام': 4.8,
            'حرم امام رضا': 4.9,
            'باغ ارم': 4.5,
            'کاخ گلستان': 4.5,
            'مسجد نصیرالملک': 4.7,
            'برج آزادی': 4.4,
            'پل خواجو': 4.6,
            'خانه بروجردی‌ها': 4.4,
            'مسجد جامع یزد': 4.5
        }
        return significance_map.get(attraction_name, 3.0)
    
    def generate_culturally_aware_response(
        self, 
        intent: ExtractedIntent, 
        entities: List[IranianEntity], 
        lang: str
    ) -> str:
        
        if lang == 'fa':
            return self._generate_persian_cultural_response(intent, entities)
        else:
            return self._generate_english_cultural_response(intent, entities)
    
    def _generate_persian_cultural_response(self, intent: ExtractedIntent, entities: List[IranianEntity]) -> str:
        
        if intent.primary_intent == 'route_request':
            cities = [e for e in entities if e.entity_type == 'city']
            if len(cities) >= 2:
                return f"مسیر از {cities[0].persian_name} به {cities[1].persian_name} را برای شما پیدا می‌کنم. با توجه به فصل {intent.cultural_context.season}، بهترین زمان سفر را پیشنهاد می‌دهم."
            elif len(cities) == 1:
                return f"شما {cities[0].persian_name} را انتخاب کرده‌اید. این شهر از نظر فرهنگی اهمیت بالایی دارد. لطفاً مقصد را نیز مشخص کنید."
        
        elif intent.primary_intent == 'cultural_heritage_request':
            return "ایران دارای میراث فرهنگی غنی است. می‌توانم مکان‌های تاریخی، کاخ‌ها، مساجد و موزه‌های مهم را معرفی کنم."
        
        elif intent.primary_intent == 'religious_pilgrimage_request':
            return "برای زیارت، حرم امام رضا در مشهد و سایر زیارتگاه‌های مهم ایران را پیشنهاد می‌دهم."
        
        elif intent.primary_intent == 'seasonal_planning_request':
            season_events = intent.cultural_context.cultural_events + intent.cultural_context.religious_events
            if season_events:
                events_text = "، ".join([e['name_fa'] for e in season_events])
                return f"در فصل {intent.cultural_context.season}، رویدادهای مهمی مانند {events_text} برگزار می‌شود."
        
        return "لطفاً سوال خود را واضح‌تر مطرح کنید. من می‌توانم در مورد مسیر، جاذبه‌های فرهنگی، زیارت و برنامه‌ریزی فصلی کمک کنم."
    
    def _generate_english_cultural_response(self, intent: ExtractedIntent, entities: List[IranianEntity]) -> str:
        
        if intent.primary_intent == 'route_request':
            cities = [e for e in entities if e.entity_type == 'city']
            if len(cities) >= 2:
                return f"I'll find a route from {cities[0].english_name} to {cities[1].english_name} for you. Considering the {intent.cultural_context.season} season, I'll suggest the best travel time."
            elif len(cities) == 1:
                return f"You've selected {cities[0].english_name}. This city has high cultural significance. Please also specify the destination."
        
        elif intent.primary_intent == 'cultural_heritage_request':
            return "Iran has a rich cultural heritage. I can introduce important historical sites, palaces, mosques, and museums."
        
        elif intent.primary_intent == 'religious_pilgrimage_request':
            return "For pilgrimage, I recommend the Imam Reza Shrine in Mashhad and other important religious sites in Iran."
        
        elif intent.primary_intent == 'seasonal_planning_request':
            season_events = intent.cultural_context.cultural_events + intent.cultural_context.religious_events
            if season_events:
                events_text = ", ".join([e['name_en'] for e in season_events])
                return f"In {intent.cultural_context.season}, important events like {events_text} are held."
        
        return "Please ask your question more clearly. I can help with routes, cultural attractions, pilgrimage, and seasonal planning."
    
    def translate_with_cultural_context(self, text: str, target_lang: str) -> str:
        if target_lang == 'en':
            translated = text
            for persian, english in self.persian_to_english.items():
                translated = translated.replace(persian, english)
            return translated
        elif target_lang == 'fa':
            translated = text
            for english, persian in self.english_to_persian.items():
                translated = translated.replace(english, persian)
            return translated
        return text
    
    def get_cultural_recommendations(self, user_interests: List[str], lang: str) -> List[Dict[str, Any]]:
        recommendations = []
        
        for interest in user_interests:
            if 'historical' in interest.lower() or 'تاریخی' in interest:
                recommendations.append({
                    'category': 'historical',
                    'name_fa': 'تخت جمشید',
                    'name_en': 'Persepolis',
                    'description_fa': 'پایتخت امپراتوری هخامنشی',
                    'description_en': 'Capital of Achaemenid Empire',
                    'significance': 5.0
                })
            
            if 'religious' in interest.lower() or 'مذهبی' in interest:
                recommendations.append({
                    'category': 'religious',
                    'name_fa': 'حرم امام رضا',
                    'name_en': 'Imam Reza Shrine',
                    'description_fa': 'حرم مطهر امام رضا',
                    'description_en': 'Holy shrine of Imam Reza',
                    'significance': 4.9
                })
            
            if 'garden' in interest.lower() or 'باغ' in interest:
                recommendations.append({
                    'category': 'natural',
                    'name_fa': 'باغ ارم',
                    'name_en': 'Eram Garden',
                    'description_fa': 'باغ تاریخی و زیبای شیراز',
                    'description_en': 'Historical and beautiful garden of Shiraz',
                    'significance': 4.5
                })
        
        return recommendations 