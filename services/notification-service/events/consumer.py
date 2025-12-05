import json
import asyncio
import sys
import os

# Add the parent directory (notification-service) to sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from kafka import KafkaConsumer
from app.schemas.notification import NotificationCreate, NotificationType

def start_consumer():
    print("Notification Consumer Starting...", flush=True)
    try:
        # Listen to BOTH topics
        consumer = KafkaConsumer(
            "creator_notification",
            "business_notification",
            bootstrap_servers="localhost:9092",
            group_id="notification_service_group",
            value_deserializer=lambda x: json.loads(x.decode("utf-8")) if x else None
        )
        
        print("Notification Consumer Connected! Listening for events...", flush=True)

        for message in consumer:
            topic = message.topic
            user_id = message.value
            
            print(f"RECEIVED EVENT: Topic={topic}, UserID={user_id}", flush=True)
            
            # Simulate sending email
            if topic == "creator_notification":
                send_email(user_id, "You have a new booking request!", "Creator")
            elif topic == "business_notification":
                send_email(user_id, "Your booking has been sent!", "Business Owner")

    except Exception as e:
        print(f"Consumer Error: {e}", flush=True)

def send_email(user_id, subject, role):
    print(f"""
    ------------------------------------------------------
    [MOCK EMAIL SERVER]
    TO: User {user_id} ({role})
    SUBJECT: {subject}
    BODY: Please check your dashboard for details.
    STATUS: Sent ✅
    ------------------------------------------------------
    """, flush=True)

if __name__ == "__main__":
    start_consumer()