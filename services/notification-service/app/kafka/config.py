from app.config.settings import settings


KAFKA_BOOTSTRAP_SERVERS = (
    settings.kafka_bootstrap_servers
)

SHIPMENT_TOPIC = "shipment"

NOTIFICATION_CONSUMER_GROUP = "notification-group"