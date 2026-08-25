# Notification Service

The Notification Service is responsible for generating notifications after an order shipment is created.

It consumes shipment events from Apache Kafka, creates notification records in PostgreSQL, and simulates successful notification delivery.

In Version 2, the service also implements database-backed idempotent event processing to prevent duplicate Kafka events from creating duplicate notification records.

---

## Responsibilities

- Consume `ShipmentCreated` events
- Create notification records
- Generate notification messages
- Simulate notification delivery
- Maintain notification records
- Prevent duplicate event processing
- Maintain processed event records
- Commit Kafka offsets only after successful database processing

---

## Tech Stack

- Python 3.12
- FastAPI
- SQLAlchemy
- PostgreSQL
- Apache Kafka
- Confluent Kafka Python Client
- Docker

---

## Kafka

### Consumes

**Topic**

~~~text
shipment
~~~

**Event**

~~~json
{
    "event_id": "...",
    "event_type": "ShipmentCreated",
    "order_id": "...",
    "customer_id": 1,
    "shipment_id": "...",
    "tracking_number": "TRK-ABC12345",
    "status": "SHIPPED"
}
~~~

The `event_id` uniquely identifies the Kafka event and is used as the idempotency key.

---

## Database

### notifications

Table

~~~text
notifications
~~~

Stores:

- Notification ID
- Order ID
- Customer ID
- Notification Type
- Notification Message
- Notification Status
- Created Timestamp
- Updated Timestamp

The notification business record represents the notification generated for an order.

The notification service currently simulates notification delivery instead of integrating with an external email, SMS, or push notification provider.

---

### processed_events

Table

~~~text
processed_events
~~~

Stores:

- Event ID
- Event Type
- Order ID
- Processed Timestamp

The `event_id` column has a `UNIQUE` constraint and acts as the idempotency key within the Notification Service database.

The `processed_events` table is separate from the `notifications` table because it represents event-processing state rather than notification business data.

---

## Idempotency

The Notification Service uses database-backed idempotent event processing.

When a Kafka event is received, the service first checks whether its `event_id` already exists in the local `processed_events` table.

If the event was already processed, the event is ignored.

If it is a new event, the notification creation and the `processed_events` record are committed in the same PostgreSQL transaction.

~~~text
ShipmentCreated
       │
       ▼
Check event_id
       │
 ┌─────┴─────┐
 │           │
 ▼           ▼
Already     New Event
Processed      │
 │             ▼
 ▼       Create Notification
Skip           │
               ▼
       Insert ProcessedEvent
               │
               ▼
             COMMIT
               │
               ▼
      Commit Kafka Offset
~~~

The important guarantee is:

~~~text
Notification Business Record
          +
ProcessedEvent Insert
          │
          ▼
Same Database Transaction
~~~

If the database transaction fails, both operations are rolled back and the Kafka offset is not committed.

This allows Kafka to redeliver the event instead of losing it.

---

## Processing Flow

~~~text
ShipmentCreated
       │
       ▼
Check Idempotency
       │
       ▼
Create Notification
       │
       ▼
Set Notification Status
       │
       ▼
Insert ProcessedEvent
       │
       ▼
COMMIT
       │
       ▼
Commit Kafka Offset
~~~

The notification status is initially simulated as successfully delivered.

Example notification:

~~~text
Type:
ORDER_SHIPPED

Message:
Your order has been shipped.

Status:
SENT
~~~

---

## Project Structure

~~~text
app/
│
├── api/
├── config/
├── core/
├── db/
├── kafka/
├── models/
├── repositories/
├── schemas/
├── services/
└── main.py
~~~

---

## Run

~~~bash
uv run uvicorn app.main:app --reload --port 8006
~~~

Swagger UI

~~~text
http://localhost:8006/docs
~~~

---

## Role in Event-Driven E-Commerce Platform

The Notification Service is the final stage of the order workflow.

After the Shipment Service successfully creates a shipment, it publishes a `ShipmentCreated` event to Kafka.

The Notification Service consumes this event and generates a notification for the customer.

~~~text
OrderCreated
     │
     ▼
InventoryReserved
     │
     ▼
PaymentSucceeded
     │
     ▼
ShipmentCreated
     │
     ▼
Notification Service
     │
     ▼
Notification Created
     │
     ▼
SENT
~~~

The service is currently designed to demonstrate the event-driven notification architecture without coupling the system to an external notification provider.

---

## Version

Current Version: **v2.0.0**