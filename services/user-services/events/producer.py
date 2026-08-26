import json
import logging
import pika
from .config import get_rabbitmq_connection

logger = logging.getLogger(__name__)

def _emit_event(exchange: str, event_data: dict, log_message: str):
    try:
        connection = get_rabbitmq_connection()
        channel = connection.channel()
        
        channel.basic_publish(
            exchange=exchange,
            routing_key='', 
            body=json.dumps(event_data).encode("utf-8"),
            properties=pika.BasicProperties(
                delivery_mode=2,
            )
        )
        connection.close()
        logger.info(log_message)
    except Exception as e:
        logger.error(f"Error emitting event to {exchange}: {e}")

def emit_user_deleted(user_id: int):
    event_data = {
        "event": "user_deleted",
        "user_id": user_id
    }
    _emit_event("user_events", event_data, f"Event emitted: user_deleted for user {user_id}")

def emit_creator_profile_updated(user_id: int):
    event_data = {
        "event": "creator_profile_updated",
        "user_id": user_id
    }
    _emit_event("user_events", event_data, f"Event emitted: creator_profile_updated for user {user_id}")
