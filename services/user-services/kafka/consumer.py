import sys
from config import get_consumer

print("Consumer starting...", flush=True)
consumer = get_consumer("user_confirmation", "user_confirmation_group")
print("Consumer connected. Waiting for messages...", flush=True)

for message in consumer:
    user_id = message.value
    print(f"User confirmed: {user_id}", flush=True)