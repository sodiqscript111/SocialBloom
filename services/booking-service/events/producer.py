import json
import logging
import pika
from .config import get_rabbitmq_connection

logger = logging.getLogger(__name__)

# Reusing a single connection/channel can be tricky with BlockingConnection across threads,
# but for this simple implementation we'll open/close or use a thread-local approach.
# A simple approach for now is a new connection per publish, or a global channel if single-threaded.
# To be robust, we'll open a connection per emit.

def _emit_event(exchange: str, event_data: dict, log_message: str):
    try:
        connection = get_rabbitmq_connection()
        channel = connection.channel()
        
        channel.basic_publish(
            exchange=exchange,
            routing_key='', # Fanout doesn't need a routing key
            body=json.dumps(event_data).encode("utf-8"),
            properties=pika.BasicProperties(
                delivery_mode=2,  # make message persistent
            )
        )
        connection.close()
        logger.info(log_message)
    except Exception as e:
        logger.error(f"Error emitting event to {exchange}: {e}")

def emit_booking_created(booking_id: int, creator_id: int, business_id: int):
    event_data = {
        "event": "booking_created",
        "booking_id": booking_id,
        "creator_id": creator_id,
        "business_id": business_id
    }
    _emit_event("booking_events", event_data, f"Event emitted: booking_created for booking {booking_id}")

def emit_booking_status_changed(booking_id: int, old_status: str, new_status: str, actor_id: int):
    event_data = {
        "event": "booking_status_changed",
        "booking_id": booking_id,
        "old_status": old_status,
        "new_status": new_status,
        "actor_id": actor_id
    }
    _emit_event("booking_events", event_data, f"Event emitted: status changed {old_status} -> {new_status} for booking {booking_id}")

def emit_booking_payment_completed(booking_id: int, payment_id: int, amount: float):
    event_data = {
        "event": "booking_payment_completed",
        "booking_id": booking_id,
        "payment_id": payment_id,
        "amount": amount
    }
    _emit_event("booking_events", event_data, f"Event emitted: payment completed for booking {booking_id}")