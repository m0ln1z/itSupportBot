from sqlalchemy.orm import Session
from sqlalchemy import func, extract
from datetime import datetime, timedelta
from typing import Dict, List, Any
from collections import Counter

from app.models.conversation import Conversation

class AnalyticsService:
    """Сервис для аналитики и статистики"""
    
    def get_statistics(self, db: Session) -> Dict[str, Any]:
        """Получение общей статистики"""
        
        # Общее количество обращений
        total_conversations = db.query(Conversation).count()
        
        # Обращения за последние 24 часа
        yesterday = datetime.utcnow() - timedelta(days=1)
        recent_conversations = db.query(Conversation).filter(
            Conversation.timestamp >= yesterday
        ).count()
        
        # Обращения за последнюю неделю
        week_ago = datetime.utcnow() - timedelta(days=7)
        week_conversations = db.query(Conversation).filter(
            Conversation.timestamp >= week_ago
        ).count()
        
        # Популярные категории
        category_stats = db.query(
            Conversation.category,
            func.count(Conversation.category).label('count')
        ).group_by(Conversation.category).all()
        
        categories = {stat.category or 'general': stat.count for stat in category_stats}
        
        # Статистика по дням (последние 7 дней)
        daily_stats = self._get_daily_statistics(db, 7)
        
        # Самые активные пользователи
        user_stats = db.query(
            Conversation.user_id,
            func.count(Conversation.user_id).label('count')
        ).group_by(Conversation.user_id).order_by(
            func.count(Conversation.user_id).desc()
        ).limit(10).all()
        
        top_users = [{'user_id': stat.user_id, 'count': stat.count} for stat in user_stats]
        
        # Среднее время ответа (в секундах) - пока заглушка
        avg_response_time = 2.5
        
        return {
            'total_conversations': total_conversations,
            'recent_conversations': recent_conversations,
            'week_conversations': week_conversations,
            'categories': categories,
            'daily_stats': daily_stats,
            'top_users': top_users,
            'avg_response_time': avg_response_time,
            'sla_metrics': self._calculate_sla_metrics(db)
        }
    
    def _get_daily_statistics(self, db: Session, days: int) -> List[Dict[str, Any]]:
        """Получение статистики по дням"""
        result = []
        
        for i in range(days):
            date = datetime.utcnow() - timedelta(days=i)
            start_of_day = date.replace(hour=0, minute=0, second=0, microsecond=0)
            end_of_day = start_of_day + timedelta(days=1)
            
            count = db.query(Conversation).filter(
                Conversation.timestamp >= start_of_day,
                Conversation.timestamp < end_of_day
            ).count()
            
            result.append({
                'date': start_of_day.strftime('%Y-%m-%d'),
                'count': count
            })
        
        return list(reversed(result))  # От старых к новым
    
    def _calculate_sla_metrics(self, db: Session) -> Dict[str, Any]:
        """Расчет метрик SLA"""
        
        # Процент решенных в течение 1 часа (заглушка)
        sla_1h = 85.5
        
        # Процент решенных в течение 4 часов (заглушка)
        sla_4h = 95.2
        
        # Процент решенных в течение 24 часов (заглушка)
        sla_24h = 99.1
        
        # Средняя оценка удовлетворенности (заглушка)
        satisfaction_score = 4.3
        
        return {
            'sla_1h': sla_1h,
            'sla_4h': sla_4h,
            'sla_24h': sla_24h,
            'satisfaction_score': satisfaction_score
        }
    
    def get_category_trends(self, db: Session, days: int = 30) -> Dict[str, List[Dict[str, Any]]]:
        """Получение трендов по категориям"""
        trends = {}
        
        # Получаем все категории
        categories = db.query(Conversation.category).distinct().all()
        
        for category_row in categories:
            category = category_row.category or 'general'
            daily_data = []
            
            for i in range(days):
                date = datetime.utcnow() - timedelta(days=i)
                start_of_day = date.replace(hour=0, minute=0, second=0, microsecond=0)
                end_of_day = start_of_day + timedelta(days=1)
                
                count = db.query(Conversation).filter(
                    Conversation.category == (category if category != 'general' else None),
                    Conversation.timestamp >= start_of_day,
                    Conversation.timestamp < end_of_day
                ).count()
                
                daily_data.append({
                    'date': start_of_day.strftime('%Y-%m-%d'),
                    'count': count
                })
            
            trends[category] = list(reversed(daily_data))
        
        return trends
    
    def get_user_activity(self, db: Session, user_id: str) -> Dict[str, Any]:
        """Получение активности конкретного пользователя"""
        
        conversations = db.query(Conversation).filter(
            Conversation.user_id == user_id
        ).order_by(Conversation.timestamp.desc()).all()
        
        if not conversations:
            return {'error': 'User not found'}
        
        # Статистика по категориям для пользователя
        user_categories = Counter([conv.category or 'general' for conv in conversations])
        
        # Последние обращения
        recent_conversations = [
            {
                'id': conv.id,
                'message': conv.user_message[:100] + '...' if len(conv.user_message) > 100 else conv.user_message,
                'category': conv.category or 'general',
                'timestamp': conv.timestamp.isoformat()
            }
            for conv in conversations[:10]
        ]
        
        return {
            'user_id': user_id,
            'total_conversations': len(conversations),
            'categories': dict(user_categories),
            'recent_conversations': recent_conversations,
            'first_contact': conversations[-1].timestamp.isoformat() if conversations else None,
            'last_contact': conversations[0].timestamp.isoformat() if conversations else None
        }
