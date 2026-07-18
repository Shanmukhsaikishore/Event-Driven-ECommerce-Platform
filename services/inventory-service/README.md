# Inventory Service

The Inventory Service is responsible for validating product stock and reserving inventory after an order is created.

It consumes events from Kafka and publishes inventory status events.

---

## Responsibilities

- Consume `OrderCreated`
- Validate stock availability
- Reserve inventory
- Publish inventory events
- Maintain inventory records

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

Topic

```
orders
```

Event

```json
{
    "event_type": "OrderCreated",
    "order_id": "...",
    "customer_id": 1,
    "product_id": 2,
    "quantity": 3,
    "total_amount": 9000
}
```

---

### Produces

Topic

```
inventory
```

Success Event

```json
{
    "event_type": "InventoryReserved",
    "order_id": "...",
    "customer_id": 1,
    "product_id": 2,
    "quantity": 3,
    "total_amount": 9000
}
```

Failure Event

```json
{
    "event_type": "InventoryFailed",
    "order_id": "...",
    "reason": "Insufficient stock"
}
```

---

## Database

Table

```
inventory
```

Stores

- Product ID
- Product Name
- Available Quantity

---

## Processing Flow

```
OrderCreated
      │
      ▼
Check Inventory
      │
 ┌────┴────┐
 │         │
 ▼         ▼
Enough     Not Enough
 │          │
 ▼          ▼
Reserve     Publish Failed
 │
 ▼
Publish InventoryReserved
```

---

## Project Structure

```
app/
│
├── config/
├── consumers/
├── core/
├── db/
├── kafka/
├── models/
├── repositories/
├── schemas/
├── services/
└── main.py
```

---

## Run

```
uv run uvicorn app.main:app --reload --port 8002
```

Swagger

```
http://localhost:8002/docs
```

---

