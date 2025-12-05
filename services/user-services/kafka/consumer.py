from kafka import KafkaConsumer
from config import get_consumer

consumer = get_consumer("user_confirmation", "user_confirmation_group")

for message in consumer:
    user_id = message.value
    print(f"User confirmed: {user_id}")