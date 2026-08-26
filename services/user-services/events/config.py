import os
import pika
import logging

logger = logging.getLogger(__name__)

RABBITMQ_URL = os.getenv("RABBITMQ_URL", "amqp://guest:guest@localhost:5672/")

def get_rabbitmq_connection():
    try:
        parameters = pika.URLParameters(RABBITMQ_URL)
        connection = pika.BlockingConnection(parameters)
        return connection
    except Exception as e:
        logger.error(f"Failed to connect to RabbitMQ: {e}")
        raise

def setup_rabbitmq():
    """Declare exchanges that this service publishes to or consumes from."""
    try:
        connection = get_rabbitmq_connection()
        channel = connection.channel()
        
        # Declare the user_events exchange
        channel.exchange_declare(exchange='user_events', exchange_type='fanout')
        
        # Declare the booking_events exchange (since we consume from it)
        channel.exchange_declare(exchange='booking_events', exchange_type='fanout')
        
        connection.close()
    except Exception as e:
        logger.error(f"Failed to setup RabbitMQ exchanges: {e}")
