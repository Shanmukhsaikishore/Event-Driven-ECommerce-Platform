# Event-Driven E-Commerce Platform

## Overview

An industry-inspired **event-driven e-commerce platform** built using **Python, FastAPI, Apache Kafka, and PostgreSQL**.

The primary goal of this project is to demonstrate how independent microservices communicate asynchronously using **Apache Kafka**, enabling loose coupling, scalability, and fault isolation.

Instead of making synchronous service-to-service REST calls, each service publishes and consumes domain events through Kafka, allowing every service to operate independently.

---

## Architecture

```text
                    +----------------+
                    |     Client     |
                    +-------+--------+
                            |
                            v
                  +-------------------+
                  |   Order Service   |
                  +-------------------+
                            |
                     OrderCreated
                            |
                            v
                     +-------------+
                     |    Kafka    |
                     +-------------+
                            |
                            v
                 +---------------------+
                 | Inventory Service   |
                 +---------------------+
                    |             |
     InventoryReserved     InventoryFailed
                    |
                    v
                 +-------------+
                 |    Kafka    |
                 +-------------+
                    |
                    v
               +----------------+
               | Payment Service|
               +----------------+
                    |
             PaymentSucceeded
```

---

## Business Flow

1. Customer places an order.
2. Order Service validates and stores the order.
3. Order Service publishes an `OrderCreated` event.
4. Inventory Service consumes the event and checks stock availability.
5. If stock is available:

   * Inventory is reserved.
   * `InventoryReserved` event is published.
6. If stock is unavailable:

   * `InventoryFailed` event is published.
7. Payment Service consumes `InventoryReserved`.
8. Payment is processed (the Payment Service is simulating payment processing).
9. Payment Service publishes `PaymentSucceeded`.

---

## Microservices

| Service           | Responsibility                                               |
| ----------------- | ------------------------------------------------------------ |
| Product Service   | Manages product catalog and pricing.                         |
| Order Service     | Creates customer orders and publishes `OrderCreated` events. |
| Inventory Service | Validates inventory and publishes inventory events.          |
| Payment Service   | Processes payments and publishes payment status events.      |

---

## Technology Stack

* Python 3.12
* FastAPI
* PostgreSQL
* SQLAlchemy
* Apache Kafka (KRaft Mode)
* Docker
* Pydantic
* Uvicorn

---

## Project Structure

```text
event-driven-ecommerce/
│
├── services/
│   ├── product-service/
│   ├── order-service/
│   ├── inventory-service/
│   └── payment-service/
│
├── shared/
│
├── docs/
│
└── README.md
```

---

## Kafka Topics

| Topic     | Published By      | Consumed By       |
| --------- | ----------------- | ----------------- |
| orders    | Order Service     | Inventory Service |
| inventory | Inventory Service | Payment Service   |
| payment   | Payment Service   | Order Service     |

---

## Features

* Event-driven microservice architecture
* Asynchronous service communication using Apache Kafka
* Independent databases for each service
* Product CRUD operations
* Order creation workflow
* Inventory validation and reservation
* Structured logging for Kafka-driven services
* Clean layered architecture (API → Service → Repository → Database)

---

## Running the Project

### 1. Start Kafka

Start Kafka using Docker.

### 2. Start PostgreSQL

Ensure PostgreSQL is running and all service databases are created.

### 3. Start Services

Run each service in a separate terminal.

```bash
Product Service

uv run uvicorn app.main:app --reload
```

```bash
Order Service

uv run uvicorn app.main:app --reload
```

```bash
Inventory Service

uv run uvicorn app.main:app --reload
```

```bash
Payment Service

uv run uvicorn app.main:app --reload
```

---

## Current Implementation

✔ Product Management

✔ Order Creation

✔ Inventory Reservation

✔ Payment Processing

✔ Event Publishing

✔ Event Consumption

✔ PostgreSQL Persistence

✔ Apache Kafka Integration

---

## Future Enhancements

* Shipment Service
* Notification Service
* Analytics Service
* API Gateway
* Saga Orchestration
* Outbox Pattern
* Dead Letter Queue (DLQ)
* Retry Mechanism
* Docker Compose Deployment
* Kubernetes Deployment
* Monitoring and Observability

---

## Learning Objectives

This project demonstrates practical implementation of:

* Event-Driven Architecture (EDA)
* Apache Kafka
* Asynchronous Microservices
* Layered Architecture
* Service Isolation
---

## Author

**Shanmukh**

Built as a hands-on learning project to gain practical experience in modern Data Engineering and Event-Driven Microservices.
