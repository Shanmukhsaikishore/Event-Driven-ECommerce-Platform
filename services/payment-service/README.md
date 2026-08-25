# Payment Service

The Payment Service is responsible for consuming successful inventory reservation events, simulating payment processing, persisting payment records, and publishing payment status events.

It represents the payment stage of the event-driven workflow.

In Version 2, the Payment Service implements database-backed idempotent event processing to prevent duplicate Kafka events from creating duplicate payment records or repeating payment operations.

---

## Responsibilities

- Consume `InventoryReserved` events
- Simulate payment processing
- Persist payment records in PostgreSQL
- Update payment status
- Publish `PaymentSucceeded` events
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

    inventory

**Event**

    {
        "event_id": "...",
        "event_type": "InventoryReserved",
        "order_id": "...",
        "product_id": 2,
        "customer_id": 1,
        "quantity": 3,
        "total_amount": 9000
    }

The `event_id` uniquely identifies the Kafka event and is used as the idempotency key.

---

### Produces

**Topic**

    payment

**Event**

    {
        "event_id": "...",
        "event_type": "PaymentSucceeded",
        "order_id": "...",
        "customer_id": 1,
        "product_id": 2,
        "quantity": 3,
        "total_amount": 9000
    }

Each newly generated `PaymentSucceeded` event receives its own `event_id`.

---

## Database

Table

    payments

Stores:

- Payment ID
- Order ID
- Customer ID
- Amount
- Payment Status
- Created Timestamp
- Updated Timestamp

---

### processed_events

Table

    processed_events

Stores:

- Event ID
- Event Type
- Order ID
- Processed Timestamp

The `event_id` column has a `UNIQUE` constraint and acts as the idempotency key within the Payment Service database.

The `processed_events` table is separate from the `payments` table because it represents event-processing state rather than payment business data.

---

## Idempotency

The Payment Service uses database-backed idempotent event processing.

When an `InventoryReserved` Kafka event is received, the service first checks whether its `event_id` already exists in the local `processed_events` table.

If the event was already processed, the event is ignored.

If it is a new event, the payment business operation and the `processed_events` record are committed in the same PostgreSQL transaction.

    InventoryReserved
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
     ▼       Create Payment
    Skip          Record
                   │
                   ▼
          Insert ProcessedEvent
                   │
                   ▼
                 COMMIT
                   │
                   ▼
          Commit Kafka Offset

The important guarantee is:

    Payment Business Operation

            +

    ProcessedEvent Insert

            │

            ▼

    Same Database Transaction

If the database transaction fails, both operations are rolled back and the Kafka offset is not committed.

Kafka can therefore redeliver the event instead of losing it.

The `UNIQUE(event_id)` constraint in PostgreSQL acts as the final database-level protection against duplicate processed-event records.

---

## Processing Flow

    InventoryReserved
           │
           ▼
    Check Idempotency
           │
     ┌─────┴─────┐
     │           │
     ▼           ▼
    Already     New Event
    Processed      │
     │             ▼
     ▼       Create Payment
    Skip          Record
                   │
                   ▼
          Payment Successful
                   │
                   ▼
          Insert ProcessedEvent
                   │
                   ▼
                 COMMIT
                   │
                   ▼
        Publish PaymentSucceeded
                   │
                   ▼
          Commit Kafka Offset

---

## Project Structure

    app/
    │
    ├── api/
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

---

## Run

    uv run uvicorn app.main:app --reload --port 8003

Swagger UI

    http://localhost:8003/docs

---

## Version

Current Version: **v2.0.0**