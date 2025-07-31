from fastapi import APIRouter, Depends, HTTPException, WebSocket, WebSocketDisconnect, Query
from sqlalchemy.orm import Session
from typing import List, Dict, Any, Optional
import json
import asyncio
from datetime import datetime
import logging

from app.database import get_db
from app.services.advanced_chat_service import AdvancedChatService
from app.core.recommender import RouteRecommender
from app.schemas import ChatMessageRequest, ChatMessageResponse
from app.models import ChatMessage, User

logger = logging.getLogger(__name__)

router = APIRouter()
chat_service = AdvancedChatService()
recommender = RouteRecommender()

# Store active WebSocket connections
active_connections = {}

@router.post("/message", response_model=ChatMessageResponse)
async def process_chat_message(request: ChatMessageRequest, db: Session = Depends(get_db)):
    """پردازش پیام چت و تولید پاسخ پیشرفته"""
    try:
        # Get language from request or detect from message
        language = getattr(request, 'lang', None) or 'en'
        
        # Process message with advanced chat service
        chat_response = await chat_service.process_message(
            message=request.message,
            user_id=str(request.user_id) if request.user_id else 'anonymous',
            language=language
        )
        
        # Generate additional route information if needed
        route_info = None
        if chat_response.route_info and (chat_response.route_info.get('origin') or chat_response.route_info.get('destination')):
            route_info = await generate_route_details(chat_response.route_info, language)
        
        # Save to database if user_id provided
        chat_message = None
        if request.user_id:
            chat_message = ChatMessage(
                user_id=request.user_id,
                message=request.message,
                response=chat_response.message,
                intent=chat_response.intent,
                entities=json.dumps(chat_response.entities),
                confidence=chat_response.confidence
            )
            db.add(chat_message)
            db.commit()
            db.refresh(chat_message)
        
        return ChatMessageResponse(
            id=chat_message.id if chat_message else 0,
            message=request.message,
            response=chat_response.message,
            intent=chat_response.intent,
            entities=chat_response.entities,
            confidence=chat_response.confidence,
            suggestions=chat_response.suggestions,
            route_info=route_info,
            quick_actions=chat_response.quick_actions,
            sentiment=chat_response.sentiment,
            conversation_flow=chat_response.conversation_flow,
            follow_up_questions=chat_response.follow_up_questions,
            created_at=chat_message.created_at if chat_message else datetime.now()
        )
        
    except Exception as e:
        logger.error(f"Error processing chat message: {e}")
        raise HTTPException(status_code=500, detail=f"خطا در پردازش پیام: {str(e)}")

@router.websocket("/ws/{user_id}")
async def websocket_endpoint(websocket: WebSocket, user_id: int):
    """WebSocket endpoint for real-time chat"""
    await websocket.accept()
    active_connections[user_id] = websocket
    
    try:
        while True:
            # Receive message
            data = await websocket.receive_text()
            message_data = json.loads(data)
            
            # Process message
            language = message_data.get('lang', 'en')
            chat_response = await chat_service.process_message(
                message=message_data['message'],
                user_id=str(user_id),
                language=language
            )
            
            # Generate route details if needed
            route_info = None
            if chat_response.route_info:
                route_info = await generate_route_details(chat_response.route_info, language)
            
            # Send response
            await websocket.send_text(json.dumps({
                'message': message_data['message'],
                'response': chat_response.message,
                'intent': chat_response.intent,
                'entities': chat_response.entities,
                'confidence': chat_response.confidence,
                'suggestions': chat_response.suggestions,
                'route_info': route_info,
                'quick_actions': chat_response.quick_actions,
                'sentiment': chat_response.sentiment,
                'conversation_flow': chat_response.conversation_flow,
                'follow_up_questions': chat_response.follow_up_questions,
                'timestamp': datetime.now().isoformat()
            }))
            
    except WebSocketDisconnect:
        if user_id in active_connections:
            del active_connections[user_id]
    except Exception as e:
        logger.error(f"WebSocket error: {e}")
        if user_id in active_connections:
            del active_connections[user_id]

@router.get("/history/{user_id}")
async def get_chat_history(
    user_id: int, 
    limit: int = Query(50, ge=1, le=100),
    db: Session = Depends(get_db)
):
    """دریافت تاریخچه چت کاربر"""
    try:
        # Get from database
        messages = db.query(ChatMessage).filter(
            ChatMessage.user_id == user_id
        ).order_by(ChatMessage.created_at.desc()).limit(limit).all()
        
        # Get from memory context
        context_history = chat_service.get_chat_history(str(user_id), limit)
        
        # Combine and format
        history = []
        for msg in messages:
            history.append({
                'id': msg.id,
                'message': msg.message,
                'response': msg.response,
                'intent': msg.intent,
                'entities': json.loads(msg.entities) if msg.entities else {},
                'confidence': msg.confidence,
                'created_at': msg.created_at.isoformat()
            })
        
        return {
            'history': history,
            'context_history': context_history,
            'total_count': len(history)
        }
        
    except Exception as e:
        logger.error(f"Error getting chat history: {e}")
        raise HTTPException(status_code=500, detail=f"خطا در دریافت تاریخچه: {str(e)}")

@router.post("/clear-history/{user_id}")
async def clear_chat_history(user_id: int, db: Session = Depends(get_db)):
    """پاک کردن تاریخچه چت کاربر"""
    try:
        # Clear from database
        db.query(ChatMessage).filter(ChatMessage.user_id == user_id).delete()
        db.commit()
        
        # Clear from memory context
        chat_service.clear_chat_history(str(user_id))
        
        return {"message": "تاریخچه چت پاک شد", "success": True}
        
    except Exception as e:
        logger.error(f"Error clearing chat history: {e}")
        raise HTTPException(status_code=500, detail=f"خطا در پاک کردن تاریخچه: {str(e)}")

@router.get("/suggestions")
async def get_chat_suggestions(lang: str = Query('en', regex='^(en|fa)$')):
    """دریافت پیشنهادات چت بر اساس زبان"""
    try:
        suggestions = chat_service.suggestion_templates.get(lang, [])
        return {
            "suggestions": suggestions,
            "language": lang
        }
    except Exception as e:
        logger.error(f"Error getting suggestions: {e}")
        raise HTTPException(status_code=500, detail=f"خطا در دریافت پیشنهادات: {str(e)}")

@router.post("/preferences/{user_id}")
async def update_user_preferences(
    user_id: int,
    preferences: Dict[str, Any]
):
    """به‌روزرسانی ترجیحات کاربر"""
    try:
        success = chat_service.update_user_preferences(str(user_id), preferences)
        if success:
            return {"message": "ترجیحات به‌روزرسانی شد", "success": True}
        else:
            raise HTTPException(status_code=404, detail="کاربر یافت نشد")
    except Exception as e:
        logger.error(f"Error updating preferences: {e}")
        raise HTTPException(status_code=500, detail=f"خطا در به‌روزرسانی ترجیحات: {str(e)}")

@router.get("/context/{user_id}")
async def get_chat_context(user_id: int):
    """دریافت context چت کاربر"""
    try:
        context = chat_service.get_or_create_context(str(user_id))
        return {
            "user_id": context.user_id,
            "current_language": context.current_language,
            "conversation_count": len(context.conversation_history),
            "user_preferences": context.user_preferences,
            "conversation_flow": context.conversation_flow,
            "sentiment_score": context.sentiment_score,
            "user_satisfaction": context.user_satisfaction,
            "last_interaction": context.last_interaction.isoformat()
        }
    except Exception as e:
        logger.error(f"Error getting chat context: {e}")
        raise HTTPException(status_code=500, detail=f"خطا در دریافت context: {str(e)}")

@router.get("/sentiment/{user_id}")
async def get_user_sentiment(user_id: int):
    """دریافت تحلیل احساسات کاربر"""
    try:
        context = chat_service.get_or_create_context(str(user_id))
        recent_messages = context.conversation_history[-5:] if context.conversation_history else []
        
        sentiment_analysis = {
            "overall_sentiment": context.sentiment_score,
            "recent_messages": [
                {
                    "message": msg["message"],
                    "sentiment": msg.get("sentiment", "neutral"),
                    "timestamp": msg["timestamp"]
                }
                for msg in recent_messages
            ],
            "satisfaction_score": context.user_satisfaction
        }
        
        return sentiment_analysis
        
    except Exception as e:
        logger.error(f"Error getting user sentiment: {e}")
        raise HTTPException(status_code=500, detail=f"خطا در دریافت تحلیل احساسات: {str(e)}")

@router.post("/feedback/{user_id}")
async def submit_user_feedback(
    user_id: int,
    feedback: Dict[str, Any]
):
    """ثبت بازخورد کاربر"""
    try:
        context = chat_service.get_or_create_context(str(user_id))
        
        # Update satisfaction score
        satisfaction = feedback.get('satisfaction', 0)
        context.user_satisfaction = satisfaction
        
        # Add feedback to conversation history
        context.conversation_history.append({
            'message': feedback.get('message', ''),
            'intent': 'feedback',
            'entities': {},
            'sentiment': 'positive' if satisfaction > 0.5 else 'negative',
            'timestamp': datetime.now().isoformat(),
            'feedback_score': satisfaction
        })
        
        return {"message": "بازخورد ثبت شد", "success": True}
        
    except Exception as e:
        logger.error(f"Error submitting feedback: {e}")
        raise HTTPException(status_code=500, detail=f"خطا در ثبت بازخورد: {str(e)}")

async def generate_route_details(route_info: Dict[str, Any], language: str) -> Dict[str, Any]:
    """تولید جزئیات مسیر"""
    try:
        origin = route_info.get('origin')
        destination = route_info.get('destination')
        
        if not origin or not destination:
            return None
        
        # Get route recommendations
        routes = recommender.recommend_routes(
            origin=origin,
            destination=destination,
            preferences=route_info.get('preferences', {}),
            budget=route_info.get('budget'),
            duration_days=route_info.get('duration_days')
        )
        
        if not routes:
            return {
                'origin': origin,
                'destination': destination,
                'error': 'مسیر یافت نشد' if language == 'fa' else 'Route not found'
            }
        
        best_route = routes[0]
        
        # Format route details
        route_details = {
            'origin': origin,
            'destination': destination,
            'distance': best_route.get('distance', 0),
            'duration': best_route.get('duration', 0),
            'cost': best_route.get('cost', 0),
            'score': best_route.get('score', 0),
            'intermediate_city': best_route.get('intermediate_city'),
            'attractions_count': len(best_route.get('attractions', [])),
            'route_type': best_route.get('route_type', 'standard')
        }
        
        # Add language-specific labels
        if language == 'fa':
            route_details['labels'] = {
                'distance': 'فاصله',
                'duration': 'زمان',
                'cost': 'هزینه',
                'score': 'امتیاز',
                'km': 'کیلومتر',
                'hours': 'ساعت',
                'toman': 'تومان'
            }
        else:
            route_details['labels'] = {
                'distance': 'Distance',
                'duration': 'Duration',
                'cost': 'Cost',
                'score': 'Score',
                'km': 'km',
                'hours': 'hours',
                'toman': 'Toman'
            }
        
        return route_details
        
    except Exception as e:
        logger.error(f"Error generating route details: {e}")
        return None

@router.post("/typing/{user_id}")
async def send_typing_indicator(user_id: int):
    """ارسال نشانگر تایپ"""
    try:
        if user_id in active_connections:
            websocket = active_connections[user_id]
            await websocket.send_text(json.dumps({
                'type': 'typing',
                'timestamp': datetime.now().isoformat()
            }))
        return {"success": True}
    except Exception as e:
        logger.error(f"Error sending typing indicator: {e}")
        return {"success": False}

@router.post("/read/{user_id}")
async def mark_message_as_read(user_id: int, message_id: int, db: Session = Depends(get_db)):
    """علامت‌گذاری پیام به عنوان خوانده شده"""
    try:
        message = db.query(ChatMessage).filter(
            ChatMessage.id == message_id,
            ChatMessage.user_id == user_id
        ).first()
        
        if message:
            message.read_at = datetime.now()
            db.commit()
            return {"success": True, "message": "پیام علامت‌گذاری شد"}
        else:
            raise HTTPException(status_code=404, detail="پیام یافت نشد")
            
    except Exception as e:
        logger.error(f"Error marking message as read: {e}")
        raise HTTPException(status_code=500, detail=f"خطا در علامت‌گذاری پیام: {str(e)}")

@router.get("/stats/{user_id}")
async def get_chat_stats(user_id: int, db: Session = Depends(get_db)):
    """دریافت آمار چت کاربر"""
    try:
        # Get message count
        total_messages = db.query(ChatMessage).filter(
            ChatMessage.user_id == user_id
        ).count()
        
        # Get intent distribution
        intents = db.query(ChatMessage.intent).filter(
            ChatMessage.user_id == user_id
        ).all()
        
        intent_counts = {}
        for intent in intents:
            intent_name = intent[0] if intent[0] else 'unknown'
            intent_counts[intent_name] = intent_counts.get(intent_name, 0) + 1
        
        # Get recent activity
        recent_messages = db.query(ChatMessage).filter(
            ChatMessage.user_id == user_id
        ).order_by(ChatMessage.created_at.desc()).limit(5).all()
        
        # Get context stats
        context = chat_service.get_or_create_context(str(user_id))
        
        return {
            "total_messages": total_messages,
            "intent_distribution": intent_counts,
            "conversation_flow": context.conversation_flow,
            "sentiment_score": context.sentiment_score,
            "user_satisfaction": context.user_satisfaction,
            "recent_activity": [
                {
                    "message": msg.message,
                    "intent": msg.intent,
                    "created_at": msg.created_at.isoformat()
                }
                for msg in recent_messages
            ]
        }
        
    except Exception as e:
        logger.error(f"Error getting chat stats: {e}")
        raise HTTPException(status_code=500, detail=f"خطا در دریافت آمار: {str(e)}")

@router.get("/analytics/{user_id}")
async def get_chat_analytics(user_id: int):
    """دریافت تحلیل‌های پیشرفته چت"""
    try:
        context = chat_service.get_or_create_context(str(user_id))
        
        # Analyze conversation patterns
        conversation_analysis = {
            "total_interactions": len(context.conversation_history),
            "average_response_time": 0,  # TODO: Calculate from timestamps
            "preferred_intents": _get_preferred_intents(context.conversation_history),
            "sentiment_trend": _get_sentiment_trend(context.conversation_history),
            "conversation_flow_pattern": context.conversation_flow,
            "user_engagement_score": _calculate_engagement_score(context)
        }
        
        return conversation_analysis
        
    except Exception as e:
        logger.error(f"Error getting chat analytics: {e}")
        raise HTTPException(status_code=500, detail=f"خطا در دریافت تحلیل‌ها: {str(e)}")

def _get_preferred_intents(history: List[Dict]) -> Dict[str, int]:
    """Get user's preferred conversation intents"""
    intent_counts = {}
    for msg in history:
        intent = msg.get('intent', 'unknown')
        intent_counts[intent] = intent_counts.get(intent, 0) + 1
    return intent_counts

def _get_sentiment_trend(history: List[Dict]) -> List[Dict]:
    """Get sentiment trend over time"""
    sentiment_trend = []
    for msg in history[-10:]:  # Last 10 messages
        sentiment_trend.append({
            "sentiment": msg.get('sentiment', 'neutral'),
            "timestamp": msg['timestamp']
        })
    return sentiment_trend

def _calculate_engagement_score(context) -> float:
    """Calculate user engagement score"""
    if not context.conversation_history:
        return 0.0
    
    # Factors: message count, sentiment, conversation flow complexity
    message_count = len(context.conversation_history)
    sentiment_score = context.sentiment_score
    flow_complexity = 1.0 if context.conversation_flow != 'initial' else 0.5
    
    engagement_score = (message_count * 0.3 + sentiment_score * 0.4 + flow_complexity * 0.3)
    return min(engagement_score, 1.0) 