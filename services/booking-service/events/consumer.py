import json
import threading
from kafka import KafkaConsumer
from .config import KAFKA_BOOTSTRAP_SERVERS

def start_booking_event_consumer():
    def consume():
        try:
            consumer = KafkaConsumer(
                "user_events",
                bootstrap_servers=KAFKA_BOOTSTRAP_SERVERS,
                auto_offset_reset="earliest",
                group_id="booking_service_consumer",
                value_deserializer=lambda v: json.loads(v.decode("utf-8"))
            )
            print("Booking service consumer started. Waiting for user events...", flush=True)

            for message in consumer:
                event = message.value
                event_type = event.get("event")

                if event_type == "user_deleted":
                    user_id = event.get("user_id")
                    print(f"Received user_deleted event for user {user_id}", flush=True)

                elif event_type == "creator_profile_updated":
                    user_id = event.get("user_id")
                    print(f"Received creator_profile_updated event for user {user_id}", flush=True)

        except Exception as e:
            print(f"Error in booking event consumer: {e}", flush=True)

    thread = threading.Thread(target=consume, daemon=True)
    thread.start()
    return thread
