
# Event-Driven E-Commerce Platform

An industry-inspired **event-driven e-commerce platform** built using **Python, FastAPI, Apache Kafka, PostgreSQL, SQLAlchemy, and Docker**.

The project demonstrates how independent microservices communicate through asynchronous domain events using **Apache Kafka**, while using synchronous HTTP communication where appropriate, such as product lookup and API Gateway routing.

The current implementation is **Version 2 (v2.0.0)** and focuses on building a production-inspired event-driven architecture while keeping the system understandable and suitable for hands-on learning.

---

## Overview

The platform currently includes:

- Event-driven microservices
- Apache Kafka for asynchronous communication
- PostgreSQL database per service
- FastAPI-based REST APIs
- API Gateway
- Product Service integration
- Order lifecycle management
- Inventory reservation
- Simulated payment processing
- Shipment processing
- Customer notification processing
- Database-backed event idempotency
- Explicit Kafka offset management
- Transactional event processing
- Independent `processed_events` tracking for Kafka-consuming services

---

## Architecture

```text
                              +----------------+
                              |     Client     |
                              +-------+--------+
                                      |
                                      | HTTP
                                      v
                            +-------------------+
                            |   API Gateway     |
                            |      :8000        |
                            +---------+---------+
                                      |
                                      | HTTP
                                      v
                            +-------------------+
                            |   Order Service   |
                            |      :8001        |
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
                            |      :8003     |
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
                       +------------+------------+
                       |                         |
                       v                         v
                +---------------+        +----------------+
                | Order Service |        | Notification   |
                |    :8001      |        | Service :8006  |
                +-------+-------+        +--------+-------+
                        |                          |
                        v                          v
                    COMPLETED                    SENT
````

### Product Service Communication

The Product Service is accessed synchronously by the Order Service to retrieve current product information and pricing.

```text
Order Service
      |
      | HTTP
      v
Product Service
      |
      v
Product Database
```

The Product Service does not share its database with the Order Service.

---

## Business Flow

The successful order workflow is:

1. Customer sends an order request through the API Gateway.
2. API Gateway forwards the request to the Order Service.
3. Order Service retrieves the current product information and price from Product Service.
4. Order Service calculates the order total.
5. Order Service stores the order with status `PENDING_PAYMENT`.
6. Order Service publishes `OrderCreated` to Kafka.
7. Inventory Service consumes `OrderCreated`.
8. Inventory Service validates product stock.
9. If sufficient stock is available:

   * Inventory is reserved.
   * `InventoryReserved` is published.
10. Payment Service consumes `InventoryReserved`.
11. Payment Service simulates payment processing.
12. Payment Service stores the payment record.
13. Payment Service publishes `PaymentSucceeded`.
14. Shipment Service consumes `PaymentSucceeded`.
15. Shipment Service creates a shipment record.
16. Shipment Service publishes `ShipmentCreated`.
17. Order Service consumes `ShipmentCreated`.
18. Order Service changes the order status to `COMPLETED`.
19. Notification Service consumes `ShipmentCreated`.
20. Notification Service creates a notification record and simulates successful notification delivery.

### Successful Order Path

```text
Order Request
     |
     v
API Gateway
     |
     v
Order Service
     |
     | OrderCreated
     v
Inventory Service
     |
     | InventoryReserved
     v
Payment Service
     |
     | PaymentSucceeded
     v
Shipment Service
     |
     | ShipmentCreated
     +--------------------+
     |                    |
     v                    v
Order Service       Notification Service
     |                    |
     v                    v
 COMPLETED              SENT
```

### Inventory Failure Path

```text
Order Service
     |
     | OrderCreated
     v
Inventory Service
     |
     | Insufficient Stock
     v
InventoryFailed
```

The Inventory Service currently publishes `InventoryFailed` when sufficient stock is unavailable. A complete order failure-state workflow can be added in a future version.

---

## Order Lifecycle

The current successful order lifecycle is:

```text
PENDING_PAYMENT
       |
       | PaymentSucceeded
       v
PAYMENT_SUCCESS
       |
       | ShipmentCreated
       v
COMPLETED
```

The Order Service updates the order state based on events received from downstream services.

---

## Microservices

| Service              | Port | Responsibility                                               |
| -------------------- | ---: | ------------------------------------------------------------ |
| API Gateway          | 8000 | Entry point for client requests and request routing          |
| Order Service        | 8001 | Creates orders and manages the order lifecycle               |
| Inventory Service    | 8002 | Validates and reserves inventory                             |
| Payment Service      | 8003 | Simulates payment processing                                 |
| Shipment Service     | 8004 | Creates shipments after successful payment                   |
| Product Service      | 8005 | Manages the product catalog and provides product information |
| Notification Service | 8006 | Creates and processes customer shipment notifications        |

---

## Technology Stack

* Python 3.12
* FastAPI
* PostgreSQL 17
* SQLAlchemy 2.x
* Apache Kafka
* Confluent Kafka Python Client
* Docker
* Docker Compose
* Pydantic
* Uvicorn
* uv
* HTTPX

---

## Kafka Topics

| Topic       | Published By      | Consumed By                         |
| ----------- | ----------------- | ----------------------------------- |
| `orders`    | Order Service     | Inventory Service                   |
| `inventory` | Inventory Service | Payment Service                     |
| `payment`   | Payment Service   | Order Service, Shipment Service     |
| `shipment`  | Shipment Service  | Order Service, Notification Service |

---

## Kafka Events

### OrderCreated

Published by the Order Service after an order is created.

```json
{
  "event_id": "...",
  "event_type": "OrderCreated",
  "order_id": "...",
  "customer_id": 1,
  "product_id": 2,
  "quantity": 3,
  "total_amount": 9000
}
```

### InventoryReserved

Published by the Inventory Service when sufficient stock is available.

```json
{
  "event_id": "...",
  "event_type": "InventoryReserved",
  "order_id": "...",
  "customer_id": 1,
  "product_id": 2,
  "quantity": 3,
  "total_amount": 9000
}
```

### InventoryFailed

Published by the Inventory Service when stock is insufficient.

```json
{
  "event_id": "...",
  "event_type": "InventoryFailed",
  "order_id": "...",
  "customer_id": 1,
  "product_id": 2,
  "total_amount": 9000,
  "reason": "Insufficient stock"
}
```

### PaymentSucceeded

Published by the Payment Service after successful simulated payment processing.

```json
{
  "event_id": "...",
  "event_type": "PaymentSucceeded",
  "order_id": "...",
  "customer_id": 1,
  "product_id": 2,
  "quantity": 3,
  "total_amount": 9000
}
```

### ShipmentCreated

Published by the Shipment Service after creating a shipment.

```json
{
  "event_id": "...",
  "event_type": "ShipmentCreated",
  "order_id": "...",
  "customer_id": 1,
  "shipment_id": "...",
  "tracking_number": "...",
  "status": "SHIPPED"
}
```

Every newly generated Kafka event receives its own unique `event_id`.

---

## Idempotent Event Processing

Version 2 introduces **database-backed idempotent event processing** for Kafka-consuming services.

Each Kafka-consuming service maintains its own local `processed_events` table.

The purpose of this table is to prevent the same Kafka event from being processed more than once when Kafka redelivers an event.

### Processing Flow

```text
Kafka Event
     |
     v
Check event_id
     |
 +---+---+
 |       |
 v       v
Already  New Event
Processed   |
 |          v
 v     Begin DB Transaction
Skip         |
             v
      Business Operation
             |
             v
      Insert ProcessedEvent
             |
             v
           COMMIT
             |
             v
     Commit Kafka Offset
```

The business operation and the `processed_events` insertion occur inside the **same PostgreSQL transaction**.

### Failure Flow

```text
Business Operation
        +
ProcessedEvent Insert
        |
        v
    ROLLBACK
        |
        v
Kafka Offset Not Committed
        |
        v
Kafka Can Redeliver Event
```

This means the Kafka offset is committed only after the database transaction succeeds.

### Processing Rules

The event-processing sequence is:

1. Receive the Kafka event.
2. Check whether the `event_id` already exists in `processed_events`.
3. If it already exists, skip the event.
4. If it is a new event, begin a database transaction.
5. Perform the business operation.
6. Insert the `event_id` into `processed_events`.
7. Commit the database transaction.
8. Commit the Kafka offset.

The `event_id` column in `processed_events` has a `UNIQUE` constraint and acts as the idempotency key within the service's local database.

---

## Database-per-Service Architecture

Each service owns its own database.

```text
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
```

Services do not directly access databases owned by other services.

Communication happens through:

* Kafka events for asynchronous business workflows
* HTTP APIs for synchronous requests where appropriate

This maintains service ownership and clear data boundaries.

---

## API Gateway

The API Gateway acts as the public entry point for client requests.

Current Version 2 routing:

```text
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
```

Currently, the API Gateway forwards order creation requests to the Order Service.

The Product Service is not directly routed through the API Gateway in the current implementation.

---

## Product Service

The Product Service owns the product catalog.

It provides REST APIs for:

* Creating products
* Retrieving products
* Updating products
* Deleting products
* Internal product lookup

The Order Service uses the internal product endpoint to retrieve the current product price during order creation.

The client does not provide the product price when creating an order.

```text
Order Service
      |
      | HTTP
      v
GET /internal/products/{product_id}
      |
      v
Product Service
```

This prevents the Order Service from trusting a client-provided product price.

---

## Project Structure

```text
event-driven-ecommerce/
│
├── services/
│   ├── api-gateway/
│   ├── order-service/
│   ├── inventory-service/
│   ├── payment-service/
│   ├── shipment-service/
│   ├── product-service/
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
```

---

## Service Ports

| Service              | Port |
| -------------------- | ---: |
| API Gateway          | 8000 |
| Order Service        | 8001 |
| Inventory Service    | 8002 |
| Payment Service      | 8003 |
| Shipment Service     | 8004 |
| Product Service      | 8005 |
| Notification Service | 8006 |

---

## Running the Project

### Prerequisites

Make sure the following are installed:

* Python 3.12
* Docker
* Docker Compose
* uv

### 1. Start Infrastructure

Start PostgreSQL and Kafka:

```bash
docker compose up -d
```

Verify that the required infrastructure containers are running before starting the application services.

### 2. Start Product Service

```bash
cd services/product-service
uv run uvicorn app.main:app --reload --port 8005
```

Swagger UI:

```text
http://localhost:8005/docs
```

### 3. Start Order Service

```bash
cd services/order-service
uv run uvicorn app.main:app --reload --port 8001
```

Swagger UI:

```text
http://localhost:8001/docs
```

### 4. Start Inventory Service

```bash
cd services/inventory-service
uv run uvicorn app.main:app --reload --port 8002
```

### 5. Start Payment Service

```bash
cd services/payment-service
uv run uvicorn app.main:app --reload --port 8003
```

### 6. Start Shipment Service

```bash
cd services/shipment-service
uv run uvicorn app.main:app --reload --port 8004
```

### 7. Start Notification Service

```bash
cd services/notification-service
uv run uvicorn app.main:app --reload --port 8006
```

### 8. Start API Gateway

```bash
cd services/api-gateway
uv run uvicorn app.main:app --reload --port 8000
```

> Run each application service in a separate terminal.

---

## Complete Event Flow

```text
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
                                |
                    +-----------+-----------+
                    |                       |
                    v                       v
             Order Service          Notification Service
                :8001                       :8006
                    |                       |
                    v                       v
               COMPLETED                   SENT
```

### Product Lookup During Order Creation

The order creation process also includes synchronous HTTP communication:

```text
Client
  |
  v
API Gateway
  |
  v
Order Service
  |
  | HTTP
  v
Product Service
  |
  v
Current Product Price
  |
  v
Order Service
  |
  v
OrderCreated
  |
  v
Kafka Event Workflow
```

---

## Features

* Event-driven microservice architecture
* Apache Kafka-based asynchronous communication
* Database-per-service architecture
* Product CRUD operations
* Synchronous product lookup through HTTP
* API Gateway
* Order creation workflow
* Inventory validation
* Inventory reservation
* Inventory failure event publishing
* Simulated payment processing
* Shipment creation
* Customer notification processing
* Kafka event publishing
* Kafka event consumption
* Database-backed idempotency
* Database-local `processed_events` tracking
* Explicit Kafka offset management
* Transactional event processing
* Structured Kafka consumer logging
* Layered architecture
* Repository pattern
* Service isolation
* PostgreSQL persistence

---

## Version 2 Improvements

Version 2 extends the original implementation with:

* Product price retrieval from Product Service
* API Gateway
* Shipment Service
* Notification Service
* Complete successful order lifecycle
* Database-backed event idempotency
* `processed_events` tables for Kafka-consuming services
* Explicit Kafka offset commits
* Transactional event processing
* Separate Notification database
* Shipment and notification event propagation
* Improved service-to-service responsibilities
* Customer ID propagation through the payment-to-shipment flow

---

## Current Implementation

* Product Management
* Product Service Internal Lookup
* API Gateway
* Order Creation
* Order Lifecycle Management
* Inventory Validation
* Inventory Reservation
* Inventory Failure Event
* Payment Processing
* Shipment Creation
* Notification Processing
* Event Publishing
* Event Consumption
* PostgreSQL Persistence
* Apache Kafka Integration
* Database-per-Service Architecture
* Database-backed Idempotency
* Processed Event Tracking
* Explicit Kafka Offset Management
* Transactional Event Processing

---

## Future Enhancements

* Saga orchestration
* Transactional Outbox Pattern
* Dead Letter Queue (DLQ)
* Retry mechanism
* Failure recovery strategies
* Real email/SMS notification provider
* Authentication and authorization
* API Gateway routing for additional services
* Complete Docker Compose deployment for all application services
* Kubernetes deployment
* Monitoring and observability
* Distributed tracing
* Analytics Service

---

## Learning Objectives

This project demonstrates practical implementation of:

* Event-Driven Architecture (EDA)
* Apache Kafka
* Asynchronous microservices
* Synchronous HTTP communication
* Kafka consumer groups
* Kafka offset management
* Database-backed idempotency
* Transactional event processing
* Database-per-Service architecture
* Layered architecture
* Repository pattern
* Service isolation
* Microservice communication
* Event-driven order lifecycle management
* Failure-aware event processing

---

## Author

**Shanmukh**

Built as a hands-on learning project to gain practical experience in modern Data Engineering and Event-Driven Microservices.

---

## Version

Current Version: **v2.0.0**
