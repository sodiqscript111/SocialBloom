from kafka import KafkaProducer, KafkaConsumer

KAFKA_BOOTSTRAP_SERVERS = ["localhost:9092"]

def get_producer():
    return KafkaProducer(
        bootstrap_servers=KAFKA_BOOTSTRAP_SERVERS,
        value_serializer=lambda v: str(v).encode("utf-8"),
        retries=5,
    )

def get_consumer(topic, group_id):
    return KafkaConsumer(
        topic,
        bootstrap_servers=KAFKA_BOOTSTRAP_SERVERS,
        auto_offset_reset="earliest",
        group_id=group_id,
        value_deserializer=lambda v: v.decode("utf-8"),
    )
