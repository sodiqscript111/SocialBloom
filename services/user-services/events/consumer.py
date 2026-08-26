import json
import threading
import time
import logging
from .config import get_rabbitmq_connection, setup_rabbitmq

logger = logging.getLogger(__name__)

def start_user_event_consumer():
    def consume():
        # Ensure exchanges are setup before consuming
        setup_rabbitmq()
        
        while True:
            try:
                connection = get_rabbitmq_connection()
                channel = connection.channel()
                
                # Create a specific queue for the user service to listen to booking_events
                result = channel.queue_declare(queue='user_booking_events_queue', durable=True)
                queue_name = result.method.queue
                
                channel.queue_bind(exchange='booking_events', queue=queue_name)
                
                def callback(ch, method, properties, body):
                    try:
                        event = json.loads(body.decode("utf-8"))
                        event_type = event.get("event")

                        if event_type == "booking_created":
                            booking_id = event.get("booking_id")
                            logger.info(f"Received booking_created event for booking {booking_id}")
                            
                        # Acknowledge the message
                        ch.basic_ack(delivery_tag=method.delivery_tag)
                    except Exception as e:
                        logger.error(f"Failed to process message: {e}")
                        # Reject and requeue
                        ch.basic_nack(delivery_tag=method.delivery_tag, requeue=True)

                channel.basic_qos(prefetch_count=1)
                channel.basic_consume(queue=queue_name, on_message_callback=callback)
                
                logger.info("User service RabbitMQ consumer started. Waiting for booking events...")
                channel.start_consuming()

            except Exception as e:
                logger.error(f"Error in user event consumer: {e}. Retrying in 5s...")
                time.sleep(5)

    thread = threading.Thread(target=consume, daemon=True)
    thread.start()
    return thread