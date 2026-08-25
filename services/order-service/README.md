# Order Service

The Order Service is responsible for creating customer orders, persisting them in PostgreSQL, and initiating the event-driven workflow by publishing order events to Apache Kafka.

It acts as the entry point for the order lifecycle in the e-commerce platform.

In Version 2, the Order Service retrieves product pricing from the Product Service, consumes payment and shipment events, maintains the order lifecycle, and implements database-backed idempotent event processing.

---

## Responsibilities

- Create new customer orders
- Retrieve product information from Product Service
- Calculate order total amount
- Persist orders in PostgreSQL
- Publish `OrderCreated` events to Kafka
- Consume `PaymentSucceeded` events
- Consume `ShipmentCreated` events
- Maintain the order lifecycle
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

## API

### Create Order

**POST**

    /orders

Example Request

    {
        "customer_id": 1,
        "product_id": 2,
        "quantity": 3
    }

The `unit_price` is not accepted from the client in Version 2.

The Order Service retrieves the current product information and price from the Product Service before creating the order.

Example Response

    {
        "order_id": "9e54ca34-4c31-47d2-be63-3d745722eb12",
        "customer_id": 1,
        "product_id": 2,
        "quantity": 3,
        "unit_price": 3000,
        "total_amount": 9000,
        "status": "PENDING_PAYMENT"
    }

---

## Product Service Communication

The Order Service communicates synchronously with the Product Service to retrieve product information.

Internal endpoint:

    GET /internal/products/{product_id}

The retrieved product price is used to calculate the order's total amount.

    Create Order
         │
         ▼
    Get Product
         │
         ▼
    Get Unit Price
         │
         ▼
    Calculate Total
         │
         ▼
    Create Order
         │
         ▼
    Publish OrderCreated

---

## Database

Table

    orders

Stores:

- Order ID
- Customer ID
- Product ID
- Quantity
- Unit Price
- Total Amount
- Order Status
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

The `event_id` column has a `UNIQUE` constraint and acts as the idempotency key within the Order Service database.

The `processed_events` table is separate from the `orders` table because it represents event-processing state rather than order business data.

---

## Kafka

### Produces

**Topic**

    orders

**Event**

    {
        "event_id": "...",
        "event_type": "OrderCreated",
        "order_id": "...",
        "customer_id": 1,
        "product_id": 2,
        "quantity": 3,
        "total_amount": 9000
    }

The `event_id` uniquely identifies the Kafka event.

Each newly generated `OrderCreated` event receives its own `event_id`.

---

### Consumes

**Payment Topic**

    payment

Current event handled:

- `PaymentSucceeded`

Example:

    {
        "event_id": "...",
        "event_type": "PaymentSucceeded",
        "order_id": "...",
        "customer_id": 1,
        "product_id": 2,
        "quantity": 3,
        "total_amount": 9000
    }

**Shipment Topic**

    shipment

Current event handled:

- `ShipmentCreated`

Example:

    {
        "event_id": "...",
        "event_type": "ShipmentCreated",
        "order_id": "...",
        "shipment_id": "...",
        "tracking_number": "...",
        "status": "SHIPPED"
    }

---

## Order Lifecycle

The Order Service maintains the order state throughout the event-driven workflow.

    Order Created
         │
         ▼
    PENDING_PAYMENT
         │
         │ PaymentSucceeded
         ▼
    PAYMENT_SUCCESS
         │
         │ ShipmentCreated
         ▼
    COMPLETED

The order is initially created with the status:

    PENDING_PAYMENT

After a successful payment event:

    PAYMENT_SUCCESS

After the shipment service creates a shipment:

    COMPLETED

---

## Idempotency

The Order Service uses database-backed idempotent event processing.

When a Kafka event is received, the service first checks whether its `event_id` already exists in the local `processed_events` table.

If the event was already processed, the event is ignored.

If it is a new event, the order state change and the `processed_events` record are committed in the same PostgreSQL transaction.

    Kafka Event
         │
         ▼
    Check event_id
         │
     ┌───┴────┐
     │        │
     ▼        ▼
    Already  New Event
    Processed   │
     │          ▼
     ▼      Find Order
    Skip        │
                ▼
          Validate Order State
                │
                ▼
           Update Order
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

    Order State Change

            +

    ProcessedEvent Insert

            │

            ▼

    Same Database Transaction

The `OrderRepository.update_status()` operation only performs the database update using `flush()` and does not commit independently.

The service commits the business operation and the `ProcessedEvent` insertion together.

If processing fails:

    Database Transaction
            │
            ▼
         ROLLBACK
            │
            ▼
    Kafka Offset NOT Committed

Kafka can therefore redeliver the event instead of the service losing it.

The `UNIQUE(event_id)` constraint in PostgreSQL acts as the final database-level protection against duplicate processed-event records.

---

## Processing Flow

### PaymentSucceeded

    PaymentSucceeded
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
     ▼        Find Order
    Skip           │
                   ▼
           Validate Order State
                   │
                   ▼
           Update Status
                   │
                   ▼
           PAYMENT_SUCCESS
                   │
                   ▼
           Insert ProcessedEvent
                   │
                   ▼
                 COMMIT
                   │
                   ▼
           Commit Kafka Offset

### ShipmentCreated

    ShipmentCreated
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
     ▼        Find Order
    Skip           │
                   ▼
           Validate Order State
                   │
                   ▼
           Update Status
                   │
                   ▼
              COMPLETED
                   │
                   ▼
           Insert ProcessedEvent
                   │
                   ▼
                 COMMIT
                   │
                   ▼
           Commit Kafka Offset

---

## Project Structure

    app/
    │
    ├── api/
    ├── clients/
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

    uv run uvicorn app.main:app --reload --port 8001

Swagger UI

    http://localhost:8001/docs

---

## Version

Current Version: **v2.0.0**