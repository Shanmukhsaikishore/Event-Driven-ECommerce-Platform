# Payment Service

The Payment Service is responsible for consuming successful inventory reservation events, simulating payment processing, persisting payment records, and publishing payment status events.

It represents the payment stage of the event-driven workflow.

---

## Responsibilities

* Consume `InventoryReserved` events
* Simulate payment processing
* Persist payment records in PostgreSQL
* Update payment status
* Publish `PaymentSucceeded` events

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
inventory
```

**Event**

```json
{
    "event_type": "InventoryReserved",
    "order_id": "...",
    "product_id": 2,
    "customer_id": 1,
    "quantity": 3,
    "total_amount": 9000
}
```

---

### Produces

**Topic**

```text
payment
```

**Event**

```json
{
	"event_type": "PaymentSucceeded",
	"order_id": "...",
	"customer_id": 1,
	"product_id": 2,
	"quantity": 4,
	"total_amount": 4000
}
```

---

## Database

Table

```text
payments
```

Stores:
* Payment ID
* Order ID
* Customer ID
* Amount
* Payment Status
* Created Timestamp
* Updated Timestamp

---

## Processing Flow

```text
InventoryReserved
        │
        ▼
Create Payment Record
        │
        ▼
Update Payment Status
        │
        ▼
Publish PaymentSucceeded
```

---

## Project Structure

```text
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
uv run uvicorn app.main:app --reload --port 8003
```

Swagger UI

```text
http://localhost:8003/docs
```
