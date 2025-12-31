from kafka import KafkaProducer
import json

from .config import get_producer

producer = get_producer()

def emit_booking_created(booking_id: int, creator_id: int, business_id: int):
    try:
        event_data = {
            "event": "booking_created",
            "booking_id": booking_id,
            "creator_id": creator_id,
            "business_id": business_id
        }
        producer.send("booking_events", value=json.dumps(event_data).encode("utf-8"))
        producer.flush()
        print(f"Event emitted: booking_created for booking {booking_id}", flush=True)
    except Exception as e:
        print(f"Error emitting booking_created event: {e}", flush=True)

def emit_booking_status_changed(booking_id: int, old_status: str, new_status: str, actor_id: int):
    try:
        event_data = {
            "event": "booking_status_changed",
            "booking_id": booking_id,
            "old_status": old_status,
            "new_status": new_status,
            "actor_id": actor_id
        }
        producer.send("booking_events", value=json.dumps(event_data).encode("utf-8"))
        producer.flush()
        print(f"Event emitted: status changed {old_status} -> {new_status} for booking {booking_id}", flush=True)
    except Exception as e:
        print(f"Error emitting booking_status_changed event: {e}", flush=True)

def emit_booking_payment_completed(booking_id: int, payment_id: int, amount: float):
    try:
        event_data = {
            "event": "booking_payment_completed",
            "booking_id": booking_id,
            "payment_id": payment_id,
            "amount": amount
        }
        producer.send("booking_events", value=json.dumps(event_data).encode("utf-8"))
        producer.flush()
        print(f"Event emitted: payment completed for booking {booking_id}", flush=True)
    except Exception as e:
        print(f"Error emitting booking_payment_completed event: {e}", flush=True)

def creator_notification(user_id: int, booking_id: int = None, event_type: str = "new_booking"):
    try:
        event_data = {
            "user_id": user_id,
            "booking_id": booking_id,
            "event_type": event_type
        }
        producer.send("creator_notification", value=json.dumps(event_data).encode("utf-8"))
        producer.flush()
        print(f"Creator notification sent for user {user_id}", flush=True)
    except Exception as e:
        print(f"Error sending creator notification: {e}", flush=True)

def business_notification(user_id: int, booking_id: int = None, event_type: str = "booking_update"):
    try:
        event_data = {
            "user_id": user_id,
            "booking_id": booking_id,
            "event_type": event_type
        }
        producer.send("business_notification", value=json.dumps(event_data).encode("utf-8"))
        producer.flush()
        print(f"Business notification sent for user {user_id}", flush=True)
    except Exception as e:
        print(f"Error sending business notification: {e}", flush=True)