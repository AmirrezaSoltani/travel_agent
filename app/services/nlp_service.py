import re
import spacy
import nltk
from typing import Dict, List, Tuple, Optional
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords
from app.core.config import settings

class NLPService:
    def __init__(self):
        try:
            self.nlp = spacy.load(settings.spacy_model)
        except OSError:
            # Fallback to basic processing if spaCy model not available
            self.nlp = None
        
        # Download NLTK data if not available
        try:
            nltk.data.find('tokenizers/punkt')
        except LookupError:
            nltk.download('punkt')
        
        try:
            nltk.data.find('corpora/stopwords')
        except LookupError:
            nltk.download('stopwords')
        
        self.stop_words = set(stopwords.words('english'))
        
        # Persian stop words
        self.persian_stop_words = {
            'و', 'در', 'به', 'از', 'که', 'این', 'آن', 'با', 'برای', 'تا', 'را', 'است', 'بود', 'شد',
            'می', 'های', 'های', 'ها', 'ای', 'ی', 'ی', 'ی', 'ی', 'ی', 'ی', 'ی', 'ی', 'ی', 'ی'
        }
        
        # Intent patterns
        self.intent_patterns = {
            'route_request': [
                r'مسیر.*(?:از|به|بین).*',
                r'راه.*(?:از|به|بین).*',
                r'سفر.*(?:از|به|بین).*',
                r'برو.*(?:از|به|بین).*',
                r'route.*(?:from|to|between).*',
                r'way.*(?:from|to|between).*',
                r'travel.*(?:from|to|between).*',
                r'go.*(?:from|to|between).*'
            ],
            'budget_request': [
                r'بودجه.*',
                r'هزینه.*',
                r'قیمت.*',
                r'ارزان.*',
                r'گران.*',
                r'budget.*',
                r'cost.*',
                r'price.*',
                r'cheap.*',
                r'expensive.*'
            ],
            'time_request': [
                r'زمان.*',
                r'مدت.*',
                r'چند.*روز.*',
                r'time.*',
                r'duration.*',
                r'how.*long.*',
                r'days.*'
            ],
            'attraction_request': [
                r'جاذبه.*',
                r'دیدنی.*',
                r'مکان.*',
                r'attraction.*',
                r'place.*',
                r'sight.*',
                r'tourist.*'
            ],
            'preference_request': [
                r'ترجیح.*',
                r'سریع.*',
                r'ارزان.*',
                r'زیبا.*',
                r'آرام.*',
                r'preference.*',
                r'fast.*',
                r'cheap.*',
                r'beautiful.*',
                r'quiet.*'
            ]
        }
        
        # Entity patterns
        self.entity_patterns = {
            'city': [
                r'تهران|اصفهان|شیراز|تبریز|مشهد|یزد|کاشان|قم|کرج|اهواز',
                r'tehran|isfahan|shiraz|tabriz|mashhad|yazd|kashan|qom|karaj|ahvaz'
            ],
            'number': [
                r'\d+',
                r'یک|دو|سه|چهار|پنج|شش|هفت|هشت|نه|ده',
                r'one|two|three|four|five|six|seven|eight|nine|ten'
            ],
            'currency': [
                r'تومان|ریال|دلار|یورو',
                r'toman|rial|dollar|euro'
            ],
            'time_unit': [
                r'روز|ساعت|دقیقه|هفته',
                r'day|hour|minute|week'
            ]
        }
    
    def process_message(self, message: str) -> Dict[str, any]:
        """پردازش پیام و استخراج قصد و موجودیت‌ها"""
        
        # Normalize message
        normalized_message = self._normalize_text(message)
        
        # Extract intent
        intent = self._extract_intent(normalized_message)
        
        # Extract entities
        entities = self._extract_entities(normalized_message)
        
        # Generate response
        response = self._generate_response(intent, entities, message)
        
        return {
            'intent': intent,
            'entities': entities,
            'response': response,
            'confidence': self._calculate_confidence(intent, entities)
        }
    
    def _normalize_text(self, text: str) -> str:
        """نرمال‌سازی متن"""
        # Convert to lowercase
        text = text.lower()
        
        # Remove extra whitespace
        text = re.sub(r'\s+', ' ', text).strip()
        
        # Remove punctuation (keep some for patterns)
        text = re.sub(r'[^\w\s\-]', ' ', text)
        
        return text
    
    def _extract_intent(self, text: str) -> str:
        """استخراج قصد از متن"""
        max_score = 0
        best_intent = 'unknown'
        
        for intent, patterns in self.intent_patterns.items():
            score = 0
            for pattern in patterns:
                if re.search(pattern, text, re.IGNORECASE):
                    score += 1
            
            if score > max_score:
                max_score = score
                best_intent = intent
        
        return best_intent
    
    def _extract_entities(self, text: str) -> Dict[str, List[str]]:
        """استخراج موجودیت‌ها از متن"""
        entities = {}
        
        for entity_type, patterns in self.entity_patterns.items():
            entities[entity_type] = []
            for pattern in patterns:
                matches = re.findall(pattern, text, re.IGNORECASE)
                entities[entity_type].extend(matches)
            
            # Remove duplicates
            entities[entity_type] = list(set(entities[entity_type]))
        
        return entities
    
    def _generate_response(self, intent: str, entities: Dict[str, List[str]], original_message: str) -> str:
        """تولید پاسخ بر اساس قصد و موجودیت‌ها"""
        
        if intent == 'route_request':
            cities = entities.get('city', [])
            if len(cities) >= 2:
                return f"مسیر از {cities[0]} به {cities[1]} را برای شما پیدا می‌کنم. لطفاً ترجیحات خود را مشخص کنید."
            elif len(cities) == 1:
                return f"شما {cities[0]} را انتخاب کرده‌اید. لطفاً مقصد را نیز مشخص کنید."
            else:
                return "لطفاً مبدا و مقصد سفر خود را مشخص کنید."
        
        elif intent == 'budget_request':
            numbers = entities.get('number', [])
            currencies = entities.get('currency', [])
            if numbers:
                budget = numbers[0]
                currency = currencies[0] if currencies else "تومان"
                return f"بودجه {budget} {currency} برای سفر شما در نظر گرفته می‌شود."
            else:
                return "لطفاً بودجه مورد نظر خود را مشخص کنید."
        
        elif intent == 'time_request':
            numbers = entities.get('number', [])
            time_units = entities.get('time_unit', [])
            if numbers and time_units:
                duration = numbers[0]
                unit = time_units[0]
                return f"مدت سفر {duration} {unit} در نظر گرفته می‌شود."
            else:
                return "لطفاً مدت سفر مورد نظر خود را مشخص کنید."
        
        elif intent == 'attraction_request':
            return "جاذبه‌های گردشگری مسیر را برای شما پیدا می‌کنم."
        
        elif intent == 'preference_request':
            return "ترجیحات شما ثبت شد. مسیر مناسب را پیشنهاد می‌دهم."
        
        else:
            return "لطفاً سوال خود را واضح‌تر مطرح کنید. من می‌توانم در مورد مسیر، هزینه، زمان و جاذبه‌ها کمک کنم."
    
    def _calculate_confidence(self, intent: str, entities: Dict[str, List[str]]) -> float:
        """محاسبه اطمینان از تشخیص"""
        confidence = 0.0
        
        # Base confidence for intent
        if intent != 'unknown':
            confidence += 0.5
        
        # Additional confidence for entities
        total_entities = sum(len(entities.get(entity_type, [])) for entity_type in entities)
        if total_entities > 0:
            confidence += min(total_entities * 0.1, 0.4)
        
        return min(confidence, 1.0)
    
    def extract_route_info(self, message: str) -> Dict[str, any]:
        """استخراج اطلاعات مسیر از پیام"""
        processed = self.process_message(message)
        
        route_info = {
            'origin': None,
            'destination': None,
            'budget': None,
            'duration_days': None,
            'preferences': {}
        }
        
        # Extract cities
        cities = processed['entities'].get('city', [])
        if len(cities) >= 2:
            route_info['origin'] = cities[0]
            route_info['destination'] = cities[1]
        elif len(cities) == 1:
            route_info['origin'] = cities[0]
        
        # Extract budget
        numbers = processed['entities'].get('number', [])
        if numbers and 'budget' in processed['intent']:
            try:
                route_info['budget'] = float(numbers[0])
            except ValueError:
                pass
        
        # Extract duration
        if numbers and 'time' in processed['intent']:
            try:
                route_info['duration_days'] = int(numbers[0])
            except ValueError:
                pass
        
        # Extract preferences
        text = message.lower()
        if 'سریع' in text or 'fast' in text:
            route_info['preferences']['fastest'] = 0.8
        if 'ارزان' in text or 'cheap' in text:
            route_info['preferences']['cheapest'] = 0.8
        if 'زیبا' in text or 'beautiful' in text:
            route_info['preferences']['scenic'] = 0.8
        if 'آرام' in text or 'quiet' in text:
            route_info['preferences']['quiet'] = 0.8
        
        return route_info
    
    def is_persian(self, text: str) -> bool:
        """تشخیص زبان فارسی"""
        persian_chars = re.findall(r'[\u0600-\u06FF]', text)
        return len(persian_chars) > len(text) * 0.3
    
    def translate_to_english(self, text: str) -> str:
        """ترجمه ساده فارسی به انگلیسی (برای پردازش)"""
        # Simple translation mapping for common words
        translations = {
            'مسیر': 'route',
            'سفر': 'travel',
            'از': 'from',
            'به': 'to',
            'بین': 'between',
            'بودجه': 'budget',
            'هزینه': 'cost',
            'زمان': 'time',
            'جاذبه': 'attraction',
            'ترجیح': 'preference'
        }
        
        for persian, english in translations.items():
            text = text.replace(persian, english)
        
        return text 