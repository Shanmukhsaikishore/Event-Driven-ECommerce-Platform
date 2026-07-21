# Inventory Service

The Inventory Service is responsible for validating product stock and reserving inventory after an order is created.

It consumes order events from Apache Kafka, updates inventory records, and publishes inventory status events.

---

## Responsibilities

* Consume `OrderCreated` events
* Validate product stock availability
* Reserve inventory
* Publish inventory status events
* Maintain inventory records

---

## Tech Stack

* Python 3.12
* FastAPI
* SQLAlchemy
* PostgreSQL
* Apache Kafka
* Confluent Kafka Python Client
* Docker

---

## Kafka

### Consumes

**Topic**

```text
orders
```

**Event**

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

**Topic**

```text
inventory
```

**Success Event**

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

**Failure Event**

```json
{
    "event_type": "InventoryFailed",
    "order_id": "...",
    "product_id": 2,
    "customer_id": 1,
    "total_amount": 9000,
    "reason": "Insufficient stock"
}
```

---

## Database

Table

```text
inventory
```

Stores:

* Product ID
* Product Name
* Available Quantity
* Reserved Quantity

---

## Processing Flow

```text
OrderCreated
      │
      ▼
Validate Stock
      │
 ┌────┴────┐
 │         │
 ▼         ▼
Enough     Not Enough
 │          │
 ▼          ▼
Reserve     Publish InventoryFailed
 │
 ▼
Publish InventoryReserved
```

---

## Project Structure

```text
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
```

---

## Run

```bash
uv run uvicorn app.main:app --reload --port 8002
```

Swagger UI

```text
http://localhost:8002/docs
```
