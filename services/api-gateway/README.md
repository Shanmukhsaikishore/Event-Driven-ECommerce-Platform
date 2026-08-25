# Event-Driven E-Commerce Platform

## Overview

An industry-inspired **event-driven e-commerce platform** built using **Python, FastAPI, Apache Kafka, PostgreSQL, and SQLAlchemy**.

The project demonstrates how independent microservices communicate through asynchronous domain events using **Apache Kafka**, while also using synchronous HTTP communication where appropriate, such as product lookup and API Gateway routing.

Version 2 extends the original platform with:

- Shipment processing
- Customer notification processing
- API Gateway
- Database-backed idempotent event processing
- Explicit Kafka offset management
- Independent `processed_events` state for Kafka-consuming services
- Improved order lifecycle management
- Product Service integration with Order Service

The goal is to demonstrate production-inspired event-driven patterns while keeping the system understandable and suitable for hands-on learning.

---

## Architecture

\`\`\`text
                              +----------------+
                              |     Client     |
                              +-------+--------+
                                      |
                                      v
                            +-------------------+
                            |    API Gateway    |
                            |     :8000         |
                            +---------+---------+
                                      |
                                      | HTTP
                                      v
                            +-------------------+
                            |   Order Service   |
                            |     :8001         |
                            +---------+---------+
                                      |
                              OrderCreated
                                      |
                                      v
                                +-----------+
                                |   Kafka   |
                                +-----+-----+
                                      |
                                      v
                           +---------------------+
                           | Inventory Service   |
                           |       :8002         |
                           +----------+----------+
                                      |
                              InventoryReserved
                                      |
                                      v
                                +-----------+
                                |   Kafka   |
                                +-----+-----+
                                      |
                                      v
                            +----------------+
                            | Payment Service|
                            |     :8003      |
                            +-------+--------+
                                    |
                            PaymentSucceeded
                                    |
                                    v
                              +-----------+
                              |   Kafka   |
                              +-----+-----+
                                    |
                                    v
                            +----------------+
                            | Shipment       |
                            | Service :8004  |
                            +-------+--------+
                                    |
                              ShipmentCreated
                                    |
                                    v
                              +-----------+
                              |   Kafka   |
                              +-----+-----+
                                    |
                     +--------------+--------------+
                     |                             |
                     v                             v
             +---------------+             +----------------+
             | Order Service |             | Notification   |
             |    :8001      |             | Service :8006  |
             +---------------+             +----------------+
                     |                             |
                     v                             v
                COMPLETED                    Notification
\`\`\`

The Product Service operates independently and provides product information and pricing to the Order Service through synchronous HTTP communication.

\`\`\`text
Order Service
     |
     | HTTP
     v
Product Service
     |
     v
Product Database
\`\`\`

---

## Business Flow

1. Customer sends an order request through the API Gateway.
2. API Gateway forwards the request to the Order Service.
3. Order Service retrieves the current product information and price from Product Service.
4. Order Service calculates the order total and stores the order with status `PENDING_PAYMENT`.
5. Order Service publishes an `OrderCreated` event to Kafka.
6. Inventory Service consumes `OrderCreated`.
7. Inventory Service validates product stock.
8. If sufficient stock is available:
   - Inventory is reserved.
   - `InventoryReserved` is published.
9. If stock is insufficient:
   - `InventoryFailed` is published.
10. Payment Service consumes `InventoryReserved`.
11. Payment Service simulates payment processing.
12. Payment Service stores the payment record.
13. Payment Service publishes `PaymentSucceeded`.
14. Shipment Service consumes `PaymentSucceeded`.
15. Shipment Service creates a shipment record and generates shipment information.
16. Shipment Service publishes `ShipmentCreated`.
17. Order Service consumes `ShipmentCreated` and changes the order status to `COMPLETED`.
18. Notification Service consumes `ShipmentCreated`.
19. Notification Service creates a notification record and simulates successful notification delivery.

---

## Order Lifecycle

\`\`\`text
PENDING_PAYMENT
       |
       | PaymentSucceeded
       v
PAYMENT_SUCCESS
       |
       | ShipmentCreated
       v
COMPLETED
\`\`\`

The Order Service maintains the order lifecycle based on events received from downstream services.

---

## Microservices

| Service | Port | Responsibility |
|---|---:|---|
| API Gateway | 8000 | Entry point for client requests and request routing |
| Order Service | 8001 | Creates orders and manages the order lifecycle |
| Inventory Service | 8002 | Validates and reserves inventory |
| Payment Service | 8003 | Simulates payment processing |
| Shipment Service | 8004 | Creates shipments after successful payment |
| Product Service | 8005 | Manages product catalog and provides product information |
| Notification Service | 8006 | Creates and processes customer shipment notifications |

---

## Technology Stack

- Python 3.12
- FastAPI
- PostgreSQL 17
- SQLAlchemy 2.x
- Apache Kafka
- Confluent Kafka Python Client
- Docker
- Pydantic
- Uvicorn
- uv
- HTTPX

---

## Kafka Topics

| Topic | Published By | Consumed By |
|---|---|---|
| `orders` | Order Service | Inventory Service |
| `inventory` | Inventory Service | Payment Service |
| `payment` | Payment Service | Order Service, Shipment Service |
| `shipment` | Shipment Service | Order Service, Notification Service |

---

## Kafka Events

### OrderCreated

Published by the Order Service after an order is created.

\`\`\`json
{
    "event_id": "...",
    "event_type": "OrderCreated",
    "order_id": "...",
    "customer_id": 1,
    "product_id": 2,
    "quantity": 3,
    "total_amount": 9000
}
\`\`\`

### InventoryReserved

Published by the Inventory Service when sufficient stock is available.

\`\`\`json
{
    "event_id": "...",
    "event_type": "InventoryReserved",
    "order_id": "...",
    "customer_id": 1,
    "product_id": 2,
    "quantity": 3,
    "total_amount": 9000
}
\`\`\`

### InventoryFailed

Published by the Inventory Service when stock is insufficient.

\`\`\`json
{
    "event_id": "...",
    "event_type": "InventoryFailed",
    "order_id": "...",
    "product_id": 2,
    "customer_id": 1,
    "total_amount": 9000,
    "reason": "Insufficient stock"
}
\`\`\`

### PaymentSucceeded

Published by the Payment Service after successful simulated payment processing.

\`\`\`json
{
    "event_id": "...",
    "event_type": "PaymentSucceeded",
    "order_id": "...",
    "customer_id": 1,
    "product_id": 2,
    "quantity": 3,
    "total_amount": 9000
}
\`\`\`

### ShipmentCreated

Published by the Shipment Service after creating a shipment.

\`\`\`json
{
    "event_id": "...",
    "event_type": "ShipmentCreated",
    "order_id": "...",
    "customer_id": 1,
    "shipment_id": "...",
    "tracking_number": "...",
    "status": "SHIPPED"
}
\`\`\`

Each newly generated Kafka event receives its own unique `event_id`.

---

## Version 2 Idempotency

Version 2 introduces database-backed idempotent event processing for Kafka-consuming services.

The services maintain a local `processed_events` table containing successfully processed Kafka events.

The basic processing pattern is:

\`\`\`text
Kafka Event
     |
     v
Check event_id
     |
 +---+---+
 |       |
 v       v
Already  New Event
Processed    |
 |           v
 v      Business Operation
Skip         |
             v
      Insert ProcessedEvent
             |
             v
           COMMIT
             |
             v
     Commit Kafka Offset
\`\`\`

The business operation and the `processed_events` insertion are committed within the same PostgreSQL transaction.

If the transaction fails:

\`\`\`text
Business Operation
        +
ProcessedEvent Insert
        |
        v
    ROLLBACK
        |
        v
Kafka Offset Not Committed
\`\`\`

This allows Kafka to redeliver the event instead of losing it.

The `event_id` column in `processed_events` has a `UNIQUE` constraint and acts as the idempotency key within each service's own database.

---

## Database-per-Service Architecture

Each service owns its own database.

\`\`\`text
Product Service
      |
      v
product_db

Order Service
      |
      v
order_db

Inventory Service
      |
      v
inventory_db

Payment Service
      |
      v
payment_db

Shipment Service
      |
      v
shipment_db

Notification Service
      |
      v
notification_db
\`\`\`

Services do not directly access another service's database.

Communication happens through:

- Kafka events for asynchronous business workflows
- HTTP APIs for synchronous requests where appropriate

---

## API Gateway

The API Gateway acts as the public entry point for client requests.

Current Version 2 routing:

\`\`\`text
Client
  |
  v
API Gateway :8000
  |
  | HTTP
  v
Order Service :8001
  |
  v
Create Order
\`\`\`

The API Gateway currently forwards order creation requests to the Order Service.

Product Service is not currently connected directly to the API Gateway. Product APIs remain available through the Product Service itself.

---

## Product Service

The Product Service owns the product catalog.

It provides REST APIs for:

- Creating products
- Retrieving products
- Updating products
- Deleting products
- Internal product lookup

The Order Service uses the internal product endpoint to retrieve the current product price when creating an order.

The client does not provide the product price when creating an order.

\`\`\`text
Order Service
      |
      | HTTP
      v
GET /internal/products/{product_id}
      |
      v
Product Service
\`\`\`

---

## Project Structure

\`\`\`text
event-driven-ecommerce/

│
├── services/
│   │
│   ├── api-gateway/
│   │
│   ├── order-service/
│   │
│   ├── inventory-service/
│   │
│   ├── payment-service/
│   │
│   ├── shipment-service/
│   │
│   ├── product-service/
│   │
│   └── notification-service/
│
├── shared/
│
├── docs/
│
├── infrastructure/
│
├── scripts/
│
└── README.md
\`\`\`

---

## Service Ports

| Service | Port |
|---|---:|
| API Gateway | 8000 |
| Order Service | 8001 |
| Inventory Service | 8002 |
| Payment Service | 8003 |
| Shipment Service | 8004 |
| Product Service | 8005 |
| Notification Service | 8006 |

---

## Running the Project

### 1. Start Infrastructure

Start PostgreSQL and Kafka using Docker.

\`\`\`bash
docker compose up -d
\`\`\`

Ensure the required service databases are available.

### 2. Start Product Service

\`\`\`bash
cd services/product-service
uv run uvicorn app.main:app --reload --port 8005
\`\`\`

Swagger UI:

\`\`\`text
http://localhost:8005/docs
\`\`\`

### 3. Start Order Service

\`\`\`bash
cd services/order-service
uv run uvicorn app.main:app --reload --port 8001
\`\`\`

Swagger UI:

\`\`\`text
http://localhost:8001/docs
\`\`\`

### 4. Start Inventory Service

\`\`\`bash
cd services/inventory-service
uv run uvicorn app.main:app --reload --port 8002
\`\`\`

### 5. Start Payment Service

\`\`\`bash
cd services/payment-service
uv run uvicorn app.main:app --reload --port 8003
\`\`\`

### 6. Start Shipment Service

\`\`\`bash
cd services/shipment-service
uv run uvicorn app.main:app --reload --port 8004
\`\`\`

### 7. Start Product Service

\`\`\`bash
cd services/product-service
uv run uvicorn app.main:app --reload --port 8005
\`\`\`

### 8. Start Notification Service

\`\`\`bash
cd services/notification-service
uv run uvicorn app.main:app --reload --port 8006
\`\`\`

### 9. Start API Gateway

\`\`\`bash
cd services/api-gateway
uv run uvicorn app.main:app --reload --port 8000
\`\`\`

---

## Complete Event Flow

\`\`\`text
                         Client
                           |
                           v
                    API Gateway :8000
                           |
                           | HTTP
                           v
                    Order Service :8001
                           |
                    OrderCreated
                           |
                           v
                         Kafka
                           |
                           v
                  Inventory Service :8002
                           |
                 InventoryReserved
                           |
                           v
                         Kafka
                           |
                           v
                   Payment Service :8003
                           |
                  PaymentSucceeded
                           |
                           v
                         Kafka
                           |
                           v
                   Shipment Service :8004
                           |
                   ShipmentCreated
                           |
                           v
                         Kafka
                    +------+------+
                    |             |
                    v             v
              Order Service   Notification
                    |          Service :8006
                    v             |
                COMPLETED         v
                              SENT
\`\`\`

---

## Features

- Event-driven microservice architecture
- Asynchronous service communication using Apache Kafka
- Independent database for each service
- Product CRUD operations
- Synchronous product lookup through HTTP
- API Gateway for client-facing order requests
- Order creation workflow
- Inventory validation and reservation
- Simulated payment processing
- Shipment creation
- Customer notification processing
- Database-backed idempotent event processing
- Database-local `processed_events` tracking
- Explicit Kafka offset management
- Transactional business operation and event-processing state
- Structured logging for Kafka consumers
- Clean layered architecture
- Service isolation
- PostgreSQL persistence
- Kafka event propagation

---

## Version 2 Improvements

Version 2 extends the original implementation with:

- Product price retrieval from Product Service
- API Gateway
- Shipment Service
- Notification Service
- Complete order lifecycle
- Database-backed idempotency
- `processed_events` tables for Kafka-consuming services
- Explicit Kafka offset commits
- Transactional event processing
- Separate Notification database
- Shipment and notification event propagation
- Improved service-to-service responsibilities

---

## Current Implementation

✔ Product Management

✔ Product Service internal lookup

✔ API Gateway

✔ Order Creation

✔ Order Lifecycle Management

✔ Inventory Validation

✔ Inventory Reservation

✔ Payment Processing

✔ Shipment Creation

✔ Notification Processing

✔ Event Publishing

✔ Event Consumption

✔ PostgreSQL Persistence

✔ Apache Kafka Integration

✔ Database-per-Service Architecture

✔ Database-backed Idempotency

✔ Processed Event Tracking

✔ Explicit Kafka Offset Management

---

## Future Enhancements

- Saga orchestration
- Outbox Pattern
- Dead Letter Queue (DLQ)
- Retry mechanism
- Failure recovery strategies
- Real email/SMS notification provider
- Authentication and authorization
- API Gateway routing for additional services
- Docker Compose deployment for the complete platform
- Kubernetes deployment
- Monitoring and observability
- Distributed tracing
- Analytics Service

---

## Learning Objectives

This project demonstrates practical implementation of:

- Event-Driven Architecture (EDA)
- Apache Kafka
- Asynchronous Microservices
- Synchronous HTTP communication
- Kafka consumer groups
- Kafka offset management
- Database-backed idempotency
- Transactional event processing
- Database-per-Service architecture
- Layered Architecture
- Repository Pattern
- Service Isolation
- Microservice communication
- Event-driven order lifecycle management

---

## Author

**Shanmukh**

Built as a hands-on learning project to gain practical experience in modern Data Engineering and Event-Driven Microservices.

---

## Version

Current Version: **v2.0.0**