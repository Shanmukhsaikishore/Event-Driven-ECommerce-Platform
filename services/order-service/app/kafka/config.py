from app.config.settings import settings

KAFKA_BOOTSTRAP_SERVERS = settings.kafka_bootstrap_servers
KAFKA_ORDER_TOPIC = "orders"
PAYMENT_TOPIC = "payment"
SHIPMENT_TOPIC = "shipment"
ORDER_CONSUMER_GROUP = "order-group"
