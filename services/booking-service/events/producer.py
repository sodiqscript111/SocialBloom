from kafka import KafkaProducer

from .config import get_producer

producer = get_producer()

def confirm_user(user_id):
    try:
        print(f"Attempting to send Kafka message for user {user_id}...", flush=True)
        producer.send("user_confirmation", value=user_id)
        producer.flush()
        print(f"Kafka message sent for user {user_id}", flush=True)
    except Exception as e:
        print(f"Error sending user confirmation to Kafka: {e}", flush=True)