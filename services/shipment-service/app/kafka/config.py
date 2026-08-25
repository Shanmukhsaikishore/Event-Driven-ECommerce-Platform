from app.config.settings import settings

KAFKA_BOOTSTRAP_SERVERS = settings.kafka_bootstrap_servers

KAFKA_SHIPMENT_TOPIC = "shipment"
KAFKA_PAYMENT_TOPIC = "payment"
SHIPMENT_CONSUMER_GROUP = "shipment-group"