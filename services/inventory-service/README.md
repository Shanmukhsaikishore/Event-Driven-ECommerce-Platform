# Inventory Service

The Inventory Service is responsible for validating product stock and reserving inventory after an order is created.

It consumes order events from Apache Kafka, updates inventory records, and publishes inventory status events.

In Version 2, the service also implements database-backed idempotent event processing to prevent duplicate Kafka events from causing duplicate inventory operations.

---

## Responsibilities

- Consume `OrderCreated` events
- Validate product stock availability
- Reserve inventory
- Publish inventory status events
- Maintain inventory records
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
orders
~~~

**Event**

~~~json
{
    "event_id": "...",
    "event_type": "OrderCreated",
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
inventory
~~~

**Success Event**

~~~json
{
    "event_id": "...",
    "event_type": "InventoryReserved",
    "order_id": "...",
    "customer_id": 1,
    "product_id": 2,
    "quantity": 3,
    "total_amount": 9000
}
~~~

**Failure Event**

~~~json
{
    "event_id": "...",
    "event_type": "InventoryFailed",
    "order_id": "...",
    "product_id": 2,
    "customer_id": 1,
    "total_amount": 9000,
    "reason": "Insufficient stock"
}
~~~

Each newly generated event receives its own `event_id`.

---

## Database

Table

~~~text
inventory
~~~

Stores:

- Product ID
- Product Name
- Available Quantity
- Reserved Quantity

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

The `event_id` column has a `UNIQUE` constraint and acts as the idempotency key within the Inventory Service database.

The `processed_events` table is separate from the business tables because it represents event-processing state rather than inventory business data.

---

## Idempotency

The Inventory Service uses database-backed idempotent event processing.

When a Kafka event is received, the service first checks whether its `event_id` already exists in the local `processed_events` table.

If the event was already processed, the event is ignored.

If it is a new event, the inventory operation and the `processed_events` record are committed in the same PostgreSQL transaction.

~~~text
OrderCreated
      │
      ▼
Check event_id
      │
 ┌────┴────┐
 │         │
 ▼         ▼
Already   New Event
Processed    │
 │           ▼
 ▼       Validate Stock
Skip          │
             ▼
        Reserve Inventory
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
Business Operation
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
OrderCreated
      │
      ▼
Check Idempotency
      │
      ▼
Validate Stock
      │
 ┌────┴────┐
 │         │
 ▼         ▼
Enough     Not Enough
 │             │
 ▼             ▼
Reserve     Publish InventoryFailed
 │
 ▼
Insert ProcessedEvent
 │
 ▼
COMMIT
 │
 ▼
Publish InventoryReserved
 │
 ▼
Commit Kafka Offset
~~~

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
uv run uvicorn app.main:app --reload --port 8002
~~~

Swagger UI

~~~text
http://localhost:8002/docs
~~~

---

## Version

Current Version: **v2.0.0**