from app.config.settings import settings

KAFKA_BOOTSTRAP_SERVERS = settings.kafka_bootstrap_servers

PAYMENT_TOPIC = "payment"

INVENTORY_TOPIC = "inventory"

PAYMENT_CONSUMER_GROUP = "payment-group"

