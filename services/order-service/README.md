# Order Service

The Order Service is responsible for creating customer orders, persisting them in PostgreSQL, and initiating the event-driven workflow by publishing order events to Apache Kafka.

It acts as the entry point for the order lifecycle in the e-commerce platform.

---

## Responsibilities

* Create new customer orders
* Persist orders in PostgreSQL
* Publish `OrderCreated` events to Kafka
* Consume payment status events
* Maintain the order lifecycle

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

> **Note:** Currently, `unit_price` is accepted in the request for simplicity. In a production system, it should be retrieved from the Product Service.

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

Stores:

* Order ID
* Customer ID
* Product ID
* Quantity
* Unit Price
* Total Amount
* Order Status
* Created Timestamp
* Updated Timestamp

---

## Kafka

### Produces

**Topic**

```
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

### Consumes

**Topic**

```
payment
```

Current event handled:

* `PaymentSucceeded`

---

## Project Structure

```
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
```

---

## Run

```bash
uv run uvicorn app.main:app --reload --port 8001
```

Swagger UI

```
http://localhost:8001/docs
```
