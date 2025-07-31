import re
import json
import asyncio
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime, timedelta
from dataclasses import dataclass
import logging

logger = logging.getLogger(__name__)

@dataclass
class ChatContext:
    user_id: str
    current_language: str = 'fa'
    conversation_history: List[Dict] = None
    user_preferences: Dict[str, Any] = None
    current_route: Dict[str, Any] = None
    last_interaction: datetime = None
    conversation_flow: str = 'initial'
    sentiment_score: float = 0.0
    user_satisfaction: float = 0.0
    
    def __post_init__(self):
        if self.conversation_history is None:
            self.conversation_history = []
        if self.user_preferences is None:
            self.user_preferences = {}
        if self.last_interaction is None:
            self.last_interaction = datetime.now()

@dataclass
class ChatResponse:
    message: str
    intent: str
    confidence: float
    entities: Dict[str, List[str]]
    suggestions: List[str]
    route_info: Optional[Dict[str, Any]] = None
    attachments: Optional[List[Dict[str, Any]]] = None
    quick_actions: Optional[List[Dict[str, Any]]] = None
    sentiment: Optional[str] = None
    conversation_flow: Optional[str] = None
    follow_up_questions: Optional[List[str]] = None

class AdvancedChatService:
    def __init__(self):
        self.chat_contexts = {}
        self.language_patterns = self._load_language_patterns()
        self.intent_patterns = self._load_intent_patterns()
        self.entity_patterns = self._load_entity_patterns()
        self.response_templates = self._load_response_templates()
        self.suggestion_templates = self._load_suggestion_templates()
        self.conversation_flows = self._load_conversation_flows()
        self.sentiment_patterns = self._load_sentiment_patterns()
        
    def _load_language_patterns(self) -> Dict[str, re.Pattern]:
        return {
            'persian': re.compile(r'[\u0600-\u06FF\u0750-\u077F\u08A0-\u08FF\uFB50-\uFDFF\uFE70-\uFEFF]'),
            'english': re.compile(r'[a-zA-Z]'),
            'numbers': re.compile(r'\d+'),
            'currency': re.compile(r'[تت][وو][مم][اا][نن]|[رر][یی][اا][لل]|[دد][لل][اا][رر]|[یی][وو][رر][وو]')
        }
    
    def _load_intent_patterns(self) -> Dict[str, List[re.Pattern]]:
        return {
            'route_request': [
                re.compile(r'مسیر.*(?:از|به|بین)', re.IGNORECASE),
                re.compile(r'راه.*(?:از|به|بین)', re.IGNORECASE),
                re.compile(r'سفر.*(?:از|به|بین)', re.IGNORECASE),
                re.compile(r'route.*(?:from|to|between)', re.IGNORECASE),
                re.compile(r'way.*(?:from|to|between)', re.IGNORECASE),
                re.compile(r'travel.*(?:from|to|between)', re.IGNORECASE)
            ],
            'budget_request': [
                re.compile(r'بودجه|هزینه|قیمت|ارزان|گران', re.IGNORECASE),
                re.compile(r'budget|cost|price|cheap|expensive', re.IGNORECASE)
            ],
            'time_request': [
                re.compile(r'زمان|مدت|چند.*روز|ساعت', re.IGNORECASE),
                re.compile(r'time|duration|how.*long|days|hours', re.IGNORECASE)
            ],
            'attraction_request': [
                re.compile(r'جاذبه|دیدنی|مکان|تاریخی|فرهنگی', re.IGNORECASE),
                re.compile(r'attraction|place|sight|historical|cultural', re.IGNORECASE)
            ],
            'preference_request': [
                re.compile(r'ترجیح|سریع|ارزان|زیبا|آرام|لوکس', re.IGNORECASE),
                re.compile(r'preference|fast|cheap|beautiful|quiet|luxury', re.IGNORECASE)
            ],
            'greeting': [
                re.compile(r'سلام|درود|هی|hi|hello|hey', re.IGNORECASE)
            ],
            'farewell': [
                re.compile(r'خداحافظ|بای|bye|goodbye|see.*you', re.IGNORECASE)
            ],
            'thanks': [
                re.compile(r'ممنون|تشکر|مرسی|thanks|thank.*you', re.IGNORECASE)
            ],
            'help_request': [
                re.compile(r'کمک|راهنما|help|assist|guide', re.IGNORECASE)
            ],
            'complaint': [
                re.compile(r'مشکل|خطا|اشکال|complaint|problem|error', re.IGNORECASE)
            ],
            'satisfaction': [
                re.compile(r'خوب|عالی|بد|مشکل|good|excellent|bad|problem', re.IGNORECASE)
            ]
        }
    
    def _load_entity_patterns(self) -> Dict[str, List[re.Pattern]]:
        """Load entity extraction patterns"""
        return {
            'city': [
                re.compile(r'تهران|اصفهان|شیراز|تبریز|مشهد|یزد|کاشان|قم|کرج|اهواز', re.IGNORECASE),
                re.compile(r'tehran|isfahan|shiraz|tabriz|mashhad|yazd|kashan|qom|karaj|ahvaz', re.IGNORECASE)
            ],
            'number': [
                re.compile(r'\d+'),
                re.compile(r'یک|دو|سه|چهار|پنج|شش|هفت|هشت|نه|ده'),
                re.compile(r'one|two|three|four|five|six|seven|eight|nine|ten')
            ],
            'currency': [
                re.compile(r'تومان|ریال|دلار|یورو', re.IGNORECASE),
                re.compile(r'toman|rial|dollar|euro', re.IGNORECASE)
            ],
            'time_unit': [
                re.compile(r'روز|ساعت|دقیقه|هفته', re.IGNORECASE),
                re.compile(r'day|hour|minute|week', re.IGNORECASE)
            ],
            'preference': [
                re.compile(r'سریع|ارزان|زیبا|آرام|لوکس|اقتصادی', re.IGNORECASE),
                re.compile(r'fast|cheap|beautiful|quiet|luxury|economic', re.IGNORECASE)
            ]
        }
    
    def _load_sentiment_patterns(self) -> Dict[str, List[re.Pattern]]:
        """Load sentiment analysis patterns"""
        return {
            'positive': [
                re.compile(r'خوب|عالی|عالیه|ممتاز|عالی|good|excellent|great|amazing', re.IGNORECASE),
                re.compile(r'ممنون|تشکر|مرسی|thanks|thank.*you', re.IGNORECASE),
                re.compile(r'خوشحال|happy|pleased|satisfied', re.IGNORECASE)
            ],
            'negative': [
                re.compile(r'بد|بدی|مشکل|اشکال|bad|terrible|awful|problem', re.IGNORECASE),
                re.compile(r'ناراحت|عصبانی|angry|upset|frustrated', re.IGNORECASE),
                re.compile(r'مشکل|خطا|error|issue|problem', re.IGNORECASE)
            ],
            'neutral': [
                re.compile(r'متوسط|معمولی|average|normal|okay', re.IGNORECASE)
            ]
        }
    
    def _load_conversation_flows(self) -> Dict[str, Dict[str, Any]]:
        """Load conversation flow templates"""
        return {
            'route_planning': {
                'fa': {
                    'next_steps': ['بودجه', 'زمان سفر', 'ترجیحات', 'جاذبه‌ها'],
                    'questions': [
                        'بودجه مورد نظر شما چقدر است؟',
                        'چند روز می‌خواهید سفر کنید؟',
                        'آیا ترجیح خاصی دارید؟ (سریع، ارزان، زیبا)',
                        'آیا جاذبه خاصی مد نظرتان است؟'
                    ]
                },
                'en': {
                    'next_steps': ['Budget', 'Travel time', 'Preferences', 'Attractions'],
                    'questions': [
                        'What is your budget?',
                        'How many days do you want to travel?',
                        'Do you have any preferences? (fast, cheap, beautiful)',
                        'Are there specific attractions you want to see?'
                    ]
                }
            },
            'budget_discussion': {
                'fa': {
                    'next_steps': ['مسیر ارزان', 'هزینه تفصیلی', 'پیشنهادات'],
                    'questions': [
                        'آیا مسیر ارزان‌تر می‌خواهید؟',
                        'آیا هزینه تفصیلی نیاز دارید؟',
                        'آیا پیشنهادات بیشتری می‌خواهید؟'
                    ]
                },
                'en': {
                    'next_steps': ['Cheap route', 'Detailed cost', 'Suggestions'],
                    'questions': [
                        'Do you want a cheaper route?',
                        'Do you need detailed cost breakdown?',
                        'Do you want more suggestions?'
                    ]
                }
            }
        }
    
    def _load_response_templates(self) -> Dict[str, Dict[str, str]]:
        """Load response templates for different languages"""
        return {
            'fa': {
                'greeting': "سلام! 👋 من دستیار سفر هوشمند شما هستم. چطور می‌تونم کمکتون کنم؟",
                'farewell': "خوشحالم که بتونم کمکتون کنم! سفر خوشی داشته باشید! ✈️",
                'thanks': "خواهش می‌کنم! 😊 اگر سوال دیگری دارید، در خدمت هستم.",
                'help': "من می‌تونم در موارد زیر کمکتون کنم:\n\n🗺️ پیشنهاد مسیر سفر\n💰 تخمین هزینه\n⏱️ برنامه‌ریزی زمانی\n🏛️ معرفی جاذبه‌ها\n🎯 ترجیحات شخصی\n\nلطفاً سوال خود را مطرح کنید.",
                'unknown': "متوجه نشدم. لطفاً سوال خود را واضح‌تر مطرح کنید یا از منوی راهنما استفاده کنید.",
                'route_confirm': "مسیر از {origin} به {destination} را برای شما پیدا می‌کنم. لطفاً ترجیحات خود را مشخص کنید.",
                'budget_confirm': "بودجه {amount} {currency} برای سفر شما در نظر گرفته می‌شود.",
                'time_confirm': "مدت سفر {duration} {unit} در نظر گرفته می‌شود.",
                'preference_confirm': "ترجیحات شما ثبت شد. مسیر مناسب را پیشنهاد می‌دهم.",
                'complaint_response': "متأسفم که این مشکل پیش آمده. لطفاً جزئیات بیشتری ارائه دهید تا بتوانم کمک کنم.",
                'satisfaction_positive': "خوشحالم که راضی هستید! 😊",
                'satisfaction_negative': "متأسفم که راضی نیستید. لطفاً بگویید چطور می‌توانم بهتر کمک کنم.",
                'follow_up': "آیا سوال دیگری دارید؟"
            },
            'en': {
                'greeting': "Hello! 👋 I'm your smart travel assistant. How can I help you?",
                'farewell': "Glad I could help! Have a great trip! ✈️",
                'thanks': "You're welcome! 😊 If you have any other questions, I'm here to help.",
                'help': "I can help you with:\n\n🗺️ Travel route suggestions\n💰 Cost estimation\n⏱️ Time planning\n🏛️ Attraction information\n🎯 Personal preferences\n\nPlease ask your question.",
                'unknown': "I didn't understand. Please ask your question more clearly or use the help menu.",
                'route_confirm': "I'll find the route from {origin} to {destination} for you. Please specify your preferences.",
                'budget_confirm': "Budget {amount} {currency} is considered for your trip.",
                'time_confirm': "Trip duration {duration} {unit} is considered.",
                'preference_confirm': "Your preferences have been recorded. I'll suggest the appropriate route.",
                'complaint_response': "I'm sorry this issue occurred. Please provide more details so I can help.",
                'satisfaction_positive': "I'm glad you're satisfied! 😊",
                'satisfaction_negative': "I'm sorry you're not satisfied. Please tell me how I can help better.",
                'follow_up': "Do you have any other questions?"
            }
        }
    
    def _load_suggestion_templates(self) -> Dict[str, List[str]]:
        """Load suggestion templates for different languages"""
        return {
            'fa': [
                "مسیر از تهران به اصفهان",
                "بودجه 2 میلیون تومان",
                "سفر 3 روزه",
                "جاذبه‌های شیراز",
                "مسیر ارزان و سریع",
                "سفر لوکس به مشهد",
                "جاذبه‌های تاریخی اصفهان",
                "مسیر کویری یزد"
            ],
            'en': [
                "Route from Tehran to Isfahan",
                "Budget 2 million toman",
                "3-day trip",
                "Shiraz attractions",
                "Cheap and fast route",
                "Luxury trip to Mashhad",
                "Historical attractions of Isfahan",
                "Desert route to Yazd"
            ]
        }
    
    def detect_language(self, text: str) -> str:
        """Detect language of the text"""
        persian_chars = len(self.language_patterns['persian'].findall(text))
        english_chars = len(self.language_patterns['english'].findall(text))
        
        if persian_chars > english_chars:
            return 'fa'
        elif english_chars > persian_chars:
            return 'en'
        else:
            return 'fa'  # Default to Persian
    
    def analyze_sentiment(self, text: str) -> Tuple[str, float]:
        """Analyze sentiment of the text"""
        positive_score = 0
        negative_score = 0
        neutral_score = 0
        
        for pattern in self.sentiment_patterns['positive']:
            if pattern.search(text):
                positive_score += 1
        
        for pattern in self.sentiment_patterns['negative']:
            if pattern.search(text):
                negative_score += 1
        
        for pattern in self.sentiment_patterns['neutral']:
            if pattern.search(text):
                neutral_score += 1
        
        total_score = positive_score + negative_score + neutral_score
        
        if total_score == 0:
            return 'neutral', 0.0
        
        if positive_score > negative_score:
            sentiment = 'positive'
            score = positive_score / total_score
        elif negative_score > positive_score:
            sentiment = 'negative'
            score = negative_score / total_score
        else:
            sentiment = 'neutral'
            score = 0.5
        
        return sentiment, score
    
    def extract_intent(self, text: str) -> Tuple[str, float]:
        """Extract intent from text with confidence score"""
        max_score = 0
        best_intent = 'unknown'
        
        for intent, patterns in self.intent_patterns.items():
            score = 0
            for pattern in patterns:
                if pattern.search(text):
                    score += 1
            
            if score > max_score:
                max_score = score
                best_intent = intent
        
        confidence = min(max_score / 2.0, 1.0)  # Normalize confidence
        return best_intent, confidence
    
    def extract_entities(self, text: str) -> Dict[str, List[str]]:
        """Extract entities from text"""
        entities = {}
        
        for entity_type, patterns in self.entity_patterns.items():
            entities[entity_type] = []
            for pattern in patterns:
                matches = pattern.findall(text)
                entities[entity_type].extend(matches)
            
            # Remove duplicates and normalize
            entities[entity_type] = list(set(entities[entity_type]))
        
        return entities
    
    def get_contextual_suggestions(self, intent: str, entities: Dict[str, List[str]], language: str, context: ChatContext) -> List[str]:
        """Get contextual suggestions based on intent, entities, and conversation flow"""
        base_suggestions = self.suggestion_templates[language]
        
        # Get flow-based suggestions
        flow_suggestions = self._get_flow_suggestions(context.conversation_flow, language)
        
        if intent == 'route_request':
            cities = entities.get('city', [])
            if len(cities) >= 2:
                return [
                    f"بودجه برای {cities[0]} به {cities[1]}" if language == 'fa' else f"Budget for {cities[0]} to {cities[1]}",
                    f"زمان سفر {cities[0]} به {cities[1]}" if language == 'fa' else f"Travel time {cities[0]} to {cities[1]}",
                    f"جاذبه‌های {cities[1]}" if language == 'fa' else f"Attractions in {cities[1]}",
                    f"مسیر ارزان {cities[0]} به {cities[1]}" if language == 'fa' else f"Cheap route {cities[0]} to {cities[1]}"
                ]
            elif len(cities) == 1:
                return [
                    f"مقصد برای {cities[0]}" if language == 'fa' else f"Destination for {cities[0]}",
                    f"بودجه سفر به {cities[0]}" if language == 'fa' else f"Budget for trip to {cities[0]}",
                    f"زمان سفر به {cities[0]}" if language == 'fa' else f"Travel time to {cities[0]}",
                    f"جاذبه‌های {cities[0]}" if language == 'fa' else f"Attractions in {cities[0]}"
                ]
        
        elif intent == 'budget_request':
            return [
                "مسیر ارزان" if language == 'fa' else "Cheap route",
                "سفر اقتصادی" if language == 'fa' else "Economic trip",
                "هزینه هتل" if language == 'fa' else "Hotel cost",
                "هزینه غذا" if language == 'fa' else "Food cost"
            ]
        
        elif intent == 'time_request':
            return [
                "سفر کوتاه" if language == 'fa' else "Short trip",
                "سفر طولانی" if language == 'fa' else "Long trip",
                "مسیر سریع" if language == 'fa' else "Fast route",
                "توقف در مسیر" if language == 'fa' else "Stop on route"
            ]
        
        # Return flow-based suggestions if available, otherwise base suggestions
        return flow_suggestions if flow_suggestions else base_suggestions[:4]
    
    def _get_flow_suggestions(self, flow: str, language: str) -> List[str]:
        """Get suggestions based on conversation flow"""
        if flow in self.conversation_flows:
            return self.conversation_flows[flow][language]['next_steps']
        return []
    
    def _get_follow_up_questions(self, intent: str, context: ChatContext, language: str) -> List[str]:
        """Get follow-up questions based on intent and context"""
        if context.conversation_flow in self.conversation_flows:
            return self.conversation_flows[context.conversation_flow][language]['questions']
        
        # Default follow-up questions
        if intent == 'route_request':
            return [
                "بودجه مورد نظر شما چقدر است؟" if language == 'fa' else "What is your budget?",
                "چند روز می‌خواهید سفر کنید؟" if language == 'fa' else "How many days do you want to travel?"
            ]
        
        return []
    
    def _update_conversation_flow(self, intent: str, entities: Dict[str, List[str]], context: ChatContext) -> str:
        """Update conversation flow based on intent and entities"""
        if intent == 'route_request' and entities.get('city'):
            return 'route_planning'
        elif intent == 'budget_request':
            return 'budget_discussion'
        elif intent == 'greeting':
            return 'initial'
        
        return context.conversation_flow
    
    def generate_response(self, intent: str, entities: Dict[str, List[str]], language: str, context: ChatContext) -> str:
        """Generate response based on intent, entities, and context"""
        templates = self.response_templates[language]
        
        if intent == 'greeting':
            return templates['greeting']
        
        elif intent == 'farewell':
            return templates['farewell']
        
        elif intent == 'thanks':
            return templates['thanks']
        
        elif intent == 'help_request':
            return templates['help']
        
        elif intent == 'complaint':
            return templates['complaint_response']
        
        elif intent == 'satisfaction':
            if context.conversation_history:
                sentiment, _ = self.analyze_sentiment(context.conversation_history[-1]['message'])
                if sentiment == 'positive':
                    return templates['satisfaction_positive']
                else:
                    return templates['satisfaction_negative']
            else:
                return templates['satisfaction_positive']
        
        elif intent == 'route_request':
            cities = entities.get('city', [])
            if len(cities) >= 2:
                return templates['route_confirm'].format(origin=cities[0], destination=cities[1])
            elif len(cities) == 1:
                return f"شما {cities[0]} را انتخاب کرده‌اید. لطفاً مقصد را نیز مشخص کنید." if language == 'fa' else f"You selected {cities[0]}. Please specify the destination."
            else:
                return "لطفاً مبدا و مقصد سفر خود را مشخص کنید." if language == 'fa' else "Please specify your trip origin and destination."
        
        elif intent == 'budget_request':
            numbers = entities.get('number', [])
            currencies = entities.get('currency', ['تومان' if language == 'fa' else 'Toman'])
            if numbers:
                amount = numbers[0]
                currency = currencies[0]
                return templates['budget_confirm'].format(amount=amount, currency=currency)
            else:
                return "لطفاً بودجه مورد نظر خود را مشخص کنید." if language == 'fa' else "Please specify your desired budget."
        
        elif intent == 'time_request':
            numbers = entities.get('number', [])
            time_units = entities.get('time_unit', [])
            if numbers:
                duration = numbers[0]
                unit = time_units[0] if time_units else ('روز' if language == 'fa' else 'days')
                return templates['time_confirm'].format(duration=duration, unit=unit)
            else:
                return "لطفاً مدت سفر مورد نظر خود را مشخص کنید." if language == 'fa' else "Please specify your desired trip duration."
        
        elif intent == 'preference_request':
            return templates['preference_confirm']
        
        else:
            return templates['unknown']
    
    def extract_route_info(self, text: str, entities: Dict[str, List[str]]) -> Dict[str, Any]:
        """Extract route information from text and entities"""
        route_info = {
            'origin': None,
            'destination': None,
            'budget': None,
            'duration_days': None,
            'preferences': {}
        }
        
        # Extract cities
        cities = entities.get('city', [])
        if len(cities) >= 2:
            route_info['origin'] = cities[0]
            route_info['destination'] = cities[1]
        elif len(cities) == 1:
            route_info['origin'] = cities[0]
        
        # Extract budget
        numbers = entities.get('number', [])
        if numbers:
            try:
                route_info['budget'] = float(numbers[0])
            except ValueError:
                pass
        
        # Extract duration
        if numbers and entities.get('time_unit'):
            try:
                route_info['duration_days'] = int(numbers[0])
            except ValueError:
                pass
        
        # Extract preferences
        preferences = entities.get('preference', [])
        text_lower = text.lower()
        
        if 'سریع' in text_lower or 'fast' in text_lower:
            route_info['preferences']['fastest'] = 0.8
        if 'ارزان' in text_lower or 'cheap' in text_lower:
            route_info['preferences']['cheapest'] = 0.8
        if 'زیبا' in text_lower or 'beautiful' in text_lower:
            route_info['preferences']['scenic'] = 0.8
        if 'آرام' in text_lower or 'quiet' in text_lower:
            route_info['preferences']['quiet'] = 0.8
        if 'لوکس' in text_lower or 'luxury' in text_lower:
            route_info['preferences']['luxury'] = 0.8
        
        return route_info
    
    def get_or_create_context(self, user_id: str, language: str = 'fa') -> ChatContext:
        """Get or create chat context for user"""
        if user_id not in self.chat_contexts:
            self.chat_contexts[user_id] = ChatContext(
                user_id=user_id,
                current_language=language
            )
        else:
            # Update language if changed
            self.chat_contexts[user_id].current_language = language
            self.chat_contexts[user_id].last_interaction = datetime.now()
        
        return self.chat_contexts[user_id]
    
    async def process_message(self, message: str, user_id: str, language: str = 'fa') -> ChatResponse:
        """Process chat message and return structured response"""
        try:
            # Get or create context
            context = self.get_or_create_context(user_id, language)
            
            # Detect language if not provided
            if not language:
                language = self.detect_language(message)
                context.current_language = language
            
            # Analyze sentiment
            sentiment, sentiment_score = self.analyze_sentiment(message)
            context.sentiment_score = sentiment_score
            
            # Extract intent and entities
            intent, confidence = self.extract_intent(message)
            entities = self.extract_entities(message)
            
            # Update conversation flow
            new_flow = self._update_conversation_flow(intent, entities, context)
            context.conversation_flow = new_flow
            
            # Generate response
            response_text = self.generate_response(intent, entities, language, context)
            
            # Get contextual suggestions
            suggestions = self.get_contextual_suggestions(intent, entities, language, context)
            
            # Get follow-up questions
            follow_up_questions = self._get_follow_up_questions(intent, context, language)
            
            # Extract route info
            route_info = self.extract_route_info(message, entities)
            
            # Update context
            context.conversation_history.append({
                'message': message,
                'intent': intent,
                'entities': entities,
                'sentiment': sentiment,
                'timestamp': datetime.now().isoformat()
            })
            
            # Keep only last 10 messages
            if len(context.conversation_history) > 10:
                context.conversation_history = context.conversation_history[-10:]
            
            # Create quick actions based on intent
            quick_actions = self._generate_quick_actions(intent, entities, language)
            
            return ChatResponse(
                message=response_text,
                intent=intent,
                confidence=confidence,
                entities=entities,
                suggestions=suggestions,
                route_info=route_info if route_info['origin'] or route_info['destination'] else None,
                quick_actions=quick_actions,
                sentiment=sentiment,
                conversation_flow=new_flow,
                follow_up_questions=follow_up_questions
            )
            
        except Exception as e:
            logger.error(f"Error processing message: {e}")
            return ChatResponse(
                message="متأسفانه خطایی رخ داد. لطفاً دوباره تلاش کنید." if language == 'fa' else "Sorry, an error occurred. Please try again.",
                intent='error',
                confidence=0.0,
                entities={},
                suggestions=self.suggestion_templates[language][:4]
            )
    
    def _generate_quick_actions(self, intent: str, entities: Dict[str, List[str]], language: str) -> List[Dict[str, Any]]:
        """Generate quick action buttons based on intent"""
        actions = []
        
        if intent == 'route_request':
            cities = entities.get('city', [])
            if len(cities) >= 2:
                actions.append({
                    'type': 'route_search',
                    'text': 'جستجوی مسیر' if language == 'fa' else 'Search Route',
                    'data': {'origin': cities[0], 'destination': cities[1]}
                })
                actions.append({
                    'type': 'view_map',
                    'text': 'مشاهده نقشه' if language == 'fa' else 'View Map',
                    'data': {'origin': cities[0], 'destination': cities[1]}
                })
        
        if intent == 'budget_request':
            actions.append({
                'type': 'budget_calculator',
                'text': 'محاسبه‌گر هزینه' if language == 'fa' else 'Cost Calculator',
                'data': {}
            })
        
        if intent == 'attraction_request':
            actions.append({
                'type': 'attractions_list',
                'text': 'لیست جاذبه‌ها' if language == 'fa' else 'Attractions List',
                'data': {}
            })
        
        return actions
    
    def get_chat_history(self, user_id: str, limit: int = 10) -> List[Dict[str, Any]]:
        """Get chat history for user"""
        if user_id in self.chat_contexts:
            return self.chat_contexts[user_id].conversation_history[-limit:]
        return []
    
    def clear_chat_history(self, user_id: str) -> bool:
        """Clear chat history for user"""
        if user_id in self.chat_contexts:
            self.chat_contexts[user_id].conversation_history = []
            self.chat_contexts[user_id].conversation_flow = 'initial'
            return True
        return False
    
    def update_user_preferences(self, user_id: str, preferences: Dict[str, Any]) -> bool:
        """Update user preferences"""
        if user_id in self.chat_contexts:
            self.chat_contexts[user_id].user_preferences.update(preferences)
            return True
        return False 