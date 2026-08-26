from kafka import KafkaProducer
import json

from .config import get_producer

producer = get_producer()

import logging

logger = logging.getLogger(__name__)

def _emit_event(topic: str, event_data: dict, log_message: str):
    try:
        producer.send(topic, value=json.dumps(event_data).encode("utf-8"))
        producer.flush()
        logger.info(log_message)
    except Exception as e:
        logger.error(f"Error emitting event to {topic}: {e}")

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