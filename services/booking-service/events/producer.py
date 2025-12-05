from kafka import KafkaProducer

from .config import get_producer

producer = get_producer()

def creator_notification(user_id):
    try:
        print(f"Attempting to send Kafka notification for user {user_id}...", flush=True)
        producer.send("creator_notification", value=user_id)
        producer.flush()
        print(f"Kafka notification sent for creator {user_id}", flush=True)
    except Exception as e:
        print(f"Error sending creator notification to Kafka: {e}", flush=True) 

def business_notification(user_id):
    try:
        print(f"Attempting to send Kafka notification for business {user_id}...", flush=True)
        producer.send("business_notification", value=user_id)
        producer.flush()
        print(f"Kafka notification sent for business {user_id}", flush=True)
    except Exception as e:
        print(f"Error sending business notification to Kafka: {e}", flush=True) 