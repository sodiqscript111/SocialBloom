from kafka import KafkaProducer
from config import get_producer

producer = get_producer()

def confirm_user(user_id):
    try:
        producer.send("user_confirmation", value=user_id)
        producer.flush()
    except Exception as e:
        print(f"Error sending user confirmation to Kafka: {e}")