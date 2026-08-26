import json
import threading
from kafka import KafkaConsumer
from .config import KAFKA_BOOTSTRAP_SERVERS

def start_booking_event_consumer():
    def consume():
        import time
        import logging
        logger = logging.getLogger(__name__)
        
        while True:
            try:
                consumer = KafkaConsumer(
                    "user_events",
                    bootstrap_servers=KAFKA_BOOTSTRAP_SERVERS,
                    auto_offset_reset="earliest",
                    group_id="booking_service_consumer",
                    value_deserializer=lambda v: json.loads(v.decode("utf-8"))
                )
                logger.info("Booking service consumer started. Waiting for user events...")

                for message in consumer:
                    event = message.value
                    event_type = event.get("event")

                    if event_type == "user_deleted":
                        user_id = event.get("user_id")
                        logger.info(f"Received user_deleted event for user {user_id}")

                    elif event_type == "creator_profile_updated":
                        user_id = event.get("user_id")
                        logger.info(f"Received creator_profile_updated event for user {user_id}")

            except Exception as e:
                logger.error(f"Error in booking event consumer: {e}. Retrying in 5s...")
                time.sleep(5)

    thread = threading.Thread(target=consume, daemon=True)
    thread.start()
    return thread
