"""
EcoleHub Stage 4 - Analytics Service
Analytics and monitoring for Belgian school collaborative platform
"""

from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from sqlalchemy import func, and_, or_, text
import redis
import json
from prometheus_client import Counter, Histogram, Gauge, generate_latest
import logging

# Import models
from .models_stage1 import User, SELTransaction, SELService
from .models_stage2 import Message, Event, EventParticipant
from .models_stage3 import ShopProduct, ShopInterest, ShopOrder

# Prometheus metrics for EcoleHub
ecolehub_user_logins = Counter('ecolehub_user_logins_total', 'Total user logins', ['user_type'])
ecolehub_sel_transactions = Counter('ecolehub_sel_transactions_total', 'SEL transactions', ['status'])
ecolehub_shop_interests = Counter('ecolehub_shop_interests_total', 'Shop interest expressions', ['product_category'])
ecolehub_messages_sent = Counter('ecolehub_messages_sent_total', 'Messages sent', ['conversation_type'])
ecolehub_event_registrations = Counter('ecolehub_event_registrations_total', 'Event registrations', ['event_type'])

# Gauges for current state
ecolehub_active_users = Gauge('ecolehub_active_users', 'Currently active users')
ecolehub_total_families = Gauge('ecolehub_total_families', 'Total registered families')
ecolehub_sel_balance_avg = Gauge('ecolehub_sel_balance_average', 'Average SEL balance')

# Response time tracking
ecolehub_request_duration = Histogram(
    'ecolehub_request_duration_seconds',
    'Request duration for EcoleHub endpoints',
    ['method', 'endpoint', 'status']
)

class EcoleHubAnalytics:
    """
    Analytics service for Belgian school collaborative platform
    Tracks usage, engagement, and business metrics
    """
    
    def __init__(self, db: Session, redis_client: redis.Redis):
        self.db = db
        self.redis = redis_client
        
    def get_platform_overview(self) -> Dict[str, Any]:
        """Get overall platform statistics for EcoleHub."""
        try:
            # User metrics
            total_users = self.db.query(func.count(User.id)).scalar()
            active_users_week = self.db.query(func.count(User.id)).filter(
                User.created_at >= datetime.utcnow() - timedelta(days=7)
            ).scalar()
            
            # SEL system metrics
            total_services = self.db.query(func.count(SELService.id)).scalar()
            total_sel_transactions = self.db.query(func.count(SELTransaction.id)).scalar()
            avg_sel_balance = self.db.query(func.avg(SELTransaction.units)).scalar() or 0
            
            # Shop metrics
            total_products = self.db.query(func.count(ShopProduct.id)).scalar()
            total_interests = self.db.query(func.count(ShopInterest.id)).scalar()
            total_orders = self.db.query(func.count(ShopOrder.id)).scalar()
            
            # Message metrics  
            total_messages = self.db.query(func.count(Message.id)).scalar()
            messages_today = self.db.query(func.count(Message.id)).filter(
                Message.created_at >= datetime.utcnow().date()
            ).scalar()
            
            # Event metrics
            total_events = self.db.query(func.count(Event.id)).scalar()
            upcoming_events = self.db.query(func.count(Event.id)).filter(
                and_(
                    Event.start_date >= datetime.utcnow(),
                    Event.is_active == True
                )
            ).scalar()
            
            return {
                "users": {
                    "total": total_users,
                    "active_week": active_users_week,
                    "growth_rate": round((active_users_week / max(total_users, 1)) * 100, 1)
                },
                "sel": {
                    "total_services": total_services,
                    "total_transactions": total_sel_transactions,
                    "average_balance": round(avg_sel_balance, 1),
                    "engagement_rate": round((total_sel_transactions / max(total_users, 1)), 2)
                },
                "shop": {
                    "total_products": total_products,
                    "total_interests": total_interests,
                    "total_orders": total_orders,
                    "conversion_rate": round((total_orders / max(total_interests, 1)) * 100, 1)
                },
                "communication": {
                    "total_messages": total_messages,
                    "messages_today": messages_today,
                    "total_events": total_events,
                    "upcoming_events": upcoming_events
                },
                "timestamp": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logging.error(f"❌ Analytics error: {e}")
            return {"error": str(e)}
    
    def get_user_analytics(self, user_id: str) -> Dict[str, Any]:
        """Get analytics for specific user (parent)."""
        try:
            user = self.db.query(User).filter(User.id == user_id).first()
            if not user:
                return {"error": "User not found"}
            
            # SEL activity
            user_services = self.db.query(func.count(SELService.id)).filter(
                SELService.user_id == user_id
            ).scalar()
            
            user_transactions_sent = self.db.query(func.count(SELTransaction.id)).filter(
                SELTransaction.from_user_id == user_id
            ).scalar()
            
            user_transactions_received = self.db.query(func.count(SELTransaction.id)).filter(
                SELTransaction.to_user_id == user_id
            ).scalar()
            
            # Shop activity
            user_interests = self.db.query(func.count(ShopInterest.id)).filter(
                ShopInterest.user_id == user_id
            ).scalar()
            
            # Message activity
            user_messages = self.db.query(func.count(Message.id)).filter(
                Message.user_id == user_id
            ).scalar()
            
            # Event activity
            user_event_registrations = self.db.query(func.count(EventParticipant.user_id)).filter(
                EventParticipant.user_id == user_id
            ).scalar()
            
            return {
                "user_info": {
                    "name": f"{user.first_name} {user.last_name}",
                    "email": user.email,
                    "member_since": user.created_at.isoformat()
                },
                "sel_activity": {
                    "services_offered": user_services,
                    "transactions_sent": user_transactions_sent,
                    "transactions_received": user_transactions_received,
                    "engagement_score": user_services + user_transactions_sent + user_transactions_received
                },
                "shop_activity": {
                    "interests_expressed": user_interests,
                    "participation_level": "High" if user_interests > 3 else "Medium" if user_interests > 0 else "Low"
                },
                "communication": {
                    "messages_sent": user_messages,
                    "events_attended": user_event_registrations
                }
            }
            
        except Exception as e:
            logging.error(f"❌ User analytics error: {e}")
            return {"error": str(e)}
    
    def get_shop_analytics(self) -> Dict[str, Any]:
        """Analytics specific to collaborative shopping system."""
        try:
            # Product popularity
            popular_products = self.db.query(
                ShopProduct.name,
                func.count(ShopInterest.id).label('interest_count')
            ).join(ShopInterest).group_by(ShopProduct.id, ShopProduct.name).order_by(
                func.count(ShopInterest.id).desc()
            ).limit(5).all()
            
            # Category performance  
            category_stats = self.db.query(
                ShopProduct.category,
                func.count(ShopInterest.id).label('interests'),
                func.avg(ShopProduct.base_price).label('avg_price')
            ).join(ShopInterest).group_by(ShopProduct.category).all()
            
            # Order success metrics
            total_revenue = self.db.query(func.sum(ShopOrder.total_price)).filter(
                ShopOrder.status.in_(['paid', 'delivered'])
            ).scalar() or 0
            
            return {
                "popular_products": [
                    {"name": product.name, "interest_count": product.interest_count}
                    for product in popular_products
                ],
                "category_performance": [
                    {
                        "category": cat.category,
                        "interests": cat.interests,
                        "average_price": round(float(cat.avg_price), 2)
                    }
                    for cat in category_stats
                ],
                "revenue": {
                    "total": float(total_revenue),
                    "currency": "EUR"
                },
                "timestamp": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logging.error(f"❌ Shop analytics error: {e}")
            return {"error": str(e)}
    
    def get_sel_analytics(self) -> Dict[str, Any]:
        """Analytics for SEL (Local Exchange System)."""
        try:
            # Transaction volume by status
            transaction_stats = self.db.query(
                SELTransaction.status,
                func.count(SELTransaction.id).label('count'),
                func.avg(SELTransaction.units).label('avg_units')
            ).group_by(SELTransaction.status).all()
            
            # Service category popularity
            service_categories = self.db.query(
                SELService.category,
                func.count(SELService.id).label('service_count')
            ).group_by(SELService.category).order_by(
                func.count(SELService.id).desc()
            ).all()
            
            # Monthly trends
            monthly_transactions = self.db.query(
                func.date_trunc('month', SELTransaction.created_at).label('month'),
                func.count(SELTransaction.id).label('count')
            ).group_by(
                func.date_trunc('month', SELTransaction.created_at)
            ).order_by('month').limit(12).all()
            
            return {
                "transaction_status": [
                    {
                        "status": stat.status,
                        "count": stat.count,
                        "average_units": round(float(stat.avg_units), 1)
                    }
                    for stat in transaction_stats
                ],
                "service_categories": [
                    {
                        "category": cat.category,
                        "count": cat.service_count
                    }
                    for cat in service_categories
                ],
                "monthly_trends": [
                    {
                        "month": trend.month.isoformat(),
                        "transactions": trend.count
                    }
                    for trend in monthly_transactions
                ],
                "timestamp": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logging.error(f"❌ SEL analytics error: {e}")
            return {"error": str(e)}
    
    def track_user_action(self, user_id: str, action: str, details: Dict[str, Any] = None):
        """Track user action for analytics (stored in Redis)."""
        try:
            event = {
                "user_id": user_id,
                "action": action,
                "details": details or {},
                "timestamp": datetime.utcnow().isoformat(),
                "platform": "ecolehub"
            }
            
            # Store in Redis for real-time analytics
            key = f"analytics:user_actions:{datetime.utcnow().date()}"
            self.redis.lpush(key, json.dumps(event))
            self.redis.expire(key, 86400 * 30)  # Keep for 30 days
            
            # Update Prometheus metrics
            if action == 'login':
                ecolehub_user_logins.labels(user_type='parent').inc()
            elif action == 'sel_transaction':
                ecolehub_sel_transactions.labels(status=details.get('status', 'unknown')).inc()
            elif action == 'shop_interest':
                ecolehub_shop_interests.labels(product_category=details.get('category', 'unknown')).inc()
            elif action == 'message_sent':
                ecolehub_messages_sent.labels(conversation_type=details.get('type', 'unknown')).inc()
            
        except Exception as e:
            logging.error(f"❌ Action tracking error: {e}")
    
    def get_prometheus_metrics(self) -> str:
        """Get Prometheus metrics for EcoleHub."""
        try:
            # Update gauges with current values
            total_users = self.db.query(func.count(User.id)).scalar()
            ecolehub_total_families.set(total_users)
            
            # Active users (logged in last hour)
            active_count = len(self.redis.keys("session:*"))
            ecolehub_active_users.set(active_count)
            
            # Generate Prometheus metrics
            return generate_latest()
            
        except Exception as e:
            logging.error(f"❌ Prometheus metrics error: {e}")
            return f"# Error generating metrics: {e}\n"

# Global analytics service function
def get_analytics_service(db: Session, redis_client: redis.Redis) -> EcoleHubAnalytics:
    return EcoleHubAnalytics(db, redis_client)