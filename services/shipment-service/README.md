# Shipment Service

The Shipment Service is responsible for creating shipment records after a payment is successfully completed.

It consumes payment events from Apache Kafka, creates shipment records in PostgreSQL, generates tracking numbers, and publishes shipment status events.

In Version 2, the service also implements database-backed idempotent event processing to prevent duplicate Kafka events from creating duplicate shipment records.

---

## Responsibilities

- Consume `PaymentSucceeded` events
- Create shipment records
- Generate shipment tracking numbers
- Maintain shipment records
- Publish `ShipmentCreated` events to Kafka
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
payment
~~~

**Event**

~~~json
{
    "event_id": "...",
    "event_type": "PaymentSucceeded",
    "order_id": "...",
    "customer_id": 1,
    "product_id": 2,
    "quantity": 3,
    "total_amount": 9000
}
~~~

The `event_id` uniquely identifies the Kafka event and is used as the idempotency key.

---

### Produces

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
    "shipment_id": "...",
    "tracking_number": "TRK-ABC12345",
    "status": "SHIPPED"
}
~~~

Each newly generated `ShipmentCreated` event receives its own unique `event_id`.

The `ShipmentCreated` event represents the successful creation of a shipment and is consumed by downstream services such as the Order Service and Notification Service.

---

## Database

### shipments

Table

~~~text
shipments
~~~

Stores:

- Shipment ID
- Order ID
- Tracking Number
- Shipment Status
- Created Timestamp
- Updated Timestamp

The shipment record represents the shipment created for an order.

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

The `event_id` column has a `UNIQUE` constraint and acts as the idempotency key within the Shipment Service database.

The `processed_events` table is separate from the `shipments` table because it represents event-processing state rather than shipment business data.

---

## Idempotency

The Shipment Service uses database-backed idempotent event processing.

When a Kafka event is received, the service first checks whether its `event_id` already exists in the local `processed_events` table.

If the event was already processed, the event is ignored.

If it is a new event, the shipment creation and the `processed_events` record are committed in the same PostgreSQL transaction.

~~~text
PaymentSucceeded
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
 ▼       Create Shipment
Skip           │
               ▼
       Generate Tracking Number
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

The important guarantee is:

~~~text
Shipment Business Record
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
PaymentSucceeded
       │
       ▼
Check Idempotency
       │
       ▼
Create Shipment
       │
       ▼
Generate Tracking Number
       │
       ▼
Insert ProcessedEvent
       │
       ▼
COMMIT
       │
       ▼
Publish ShipmentCreated
       │
       ▼
Commit Kafka Offset
~~~

Example generated tracking number:

~~~text
TRK-ABC12345
~~~

The shipment status is generated as part of the shipment creation process and is included in the `ShipmentCreated` event.

---

## Project Structure

~~~text
app/
│
├── config/
├── core/
├── db/
├── events/
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
uv run uvicorn app.main:app --reload --port 8004
~~~

Swagger UI

~~~text
http://localhost:8004/docs
~~~

---

## Role in Event-Driven E-Commerce Platform

The Shipment Service is responsible for the shipment stage of the order workflow.

After the Payment Service successfully processes an inventory reservation, it publishes a `PaymentSucceeded` event.

The Shipment Service consumes this event, creates a shipment, generates a tracking number, and publishes a `ShipmentCreated` event.

The `ShipmentCreated` event is then consumed by downstream services such as the Order Service and Notification Service.

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
Shipment Service
     │
     ▼
ShipmentCreated
     │
 ┌───┴────────────┐
 ▼                ▼
Order Service     Notification Service
     │                │
     ▼                ▼
COMPLETED       Notification SENT
~~~

---

## Version

Current Version: **v2.0.0**