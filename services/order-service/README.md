# Order Service

The Order Service is responsible for creating customer orders and publishing order events to Kafka.

It is the entry point of the event-driven workflow.

---

## Responsibilities

- Create new customer orders
- Persist orders in PostgreSQL
- Publish `OrderCreated` events to Kafka
- Maintain order lifecycle

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

```
/orders
```

Example Request

```json
{
    "customer_id": 1,
    "product_id": 2,
    "quantity": 3,
    "unit_price": 3000
}
```

Example Response

```json
{
    "id": 1,
    "order_id": "9e54ca34-4c31-47d2-be63-3d745722eb12",
    "customer_id": 1,
    "product_id": 2,
    "quantity": 3,
    "unit_price": 3000,
    "total_amount": 9000,
    "status": "PENDING_PAYMENT"
}
```

---

## Database

Table

```
orders
```

Stores

- Order ID
- Customer ID
- Product ID
- Quantity
- Unit Price
- Total Amount
- Order Status
- Created Time
- Updated Time

---

## Kafka

### Produces

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

## Project Structure

```
app/
│
├── api/
├── config/
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
uv run uvicorn app.main:app --reload --port 8001
```

Swagger

```
http://localhost:8001/docs
```

---


