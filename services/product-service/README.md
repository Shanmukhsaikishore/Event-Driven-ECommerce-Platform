# Product Service

## Overview

The Product Service is responsible for managing the product catalog in the Event-Driven E-Commerce Platform.

It provides REST APIs for creating, retrieving, updating, and deleting products. Product browsing and product lookup remain synchronous operations through HTTP APIs in Version 2.

---

## Business Responsibility

The Product Service is responsible for:

- Managing product information
- Creating new products
- Updating product details
- Deleting products
- Retrieving product catalog
- Providing product information to other services through REST APIs

This service **does not** manage inventory, orders, payments, shipments, or notifications.

---

## Why Product Service Does Not Use Kafka

Kafka is used when business events need to be shared asynchronously between multiple independent services.

The Product Service currently does not require Kafka because:

- Product browsing is synchronous
- Product information is retrieved through REST APIs
- The Order Service retrieves product information directly when creating an order
- Product updates do not currently require event propagation

Kafka integration can be introduced in future versions if product updates need to notify other services.

---

## Architecture

~~~text
Client
   │
   ▼
FastAPI
   │
   ▼
Routes
   │
   ▼
Service Layer
   │
   ▼
Repository Layer
   │
   ▼
SQLAlchemy ORM
   │
   ▼
PostgreSQL
~~~

The Order Service communicates with the Product Service through an internal HTTP endpoint:

~~~text
Order Service
      │
      │ HTTP
      ▼
Product Service
      │
      ▼
Product Database
~~~

---

## Project Structure

~~~text
product-service/
│
├── app/
│   ├── api/
│   ├── config/
│   ├── db/
│   ├── models/
│   ├── repositories/
│   ├── schemas/
│   ├── services/
│   └── main.py
│
├── tests/
├── README.md
├── pyproject.toml
└── .env
~~~

---

## Technology Stack

- Python 3.12
- FastAPI
- PostgreSQL 17
- SQLAlchemy 2.x
- Docker
- DBeaver
- Uvicorn
- uv

---

## Database

### products

| Column | Type |
|---------|------|
| id | Integer (Primary Key) |
| name | VARCHAR(200) |
| description | TEXT |
| price | NUMERIC(10,2) |

---

## API Endpoints

| Method | Endpoint | Description |
|---------|----------|-------------|
| POST | /products | Create Product |
| GET | /products | Get All Products |
| GET | /products/{id} | Get Product by ID |
| PUT | /products/{id} | Update Product |
| DELETE | /products/{id} | Delete Product |
| GET | /internal/products/{id} | Internal product lookup |

The internal product endpoint is used by the Order Service to retrieve product information and the current product price when creating an order.

---

## How to Run

Start PostgreSQL:

~~~bash
docker compose up -d
~~~

Activate virtual environment:

~~~bash
.venv\Scripts\activate
~~~

Install dependencies:

~~~bash
uv sync
~~~

Run the service:

~~~bash
uv run uvicorn app.main:app --reload --port 8005
~~~

Swagger UI:

~~~text
http://localhost:8005/docs
~~~

---

## Design Decisions

- Layered Architecture
- Repository Pattern
- Service Layer
- Environment-based Configuration
- SQLAlchemy ORM
- RESTful API Design
- PostgreSQL as the source of truth
- Synchronous HTTP communication for product lookup

---

## Role in Event-Driven E-Commerce Platform

The Product Service owns the product catalog.

It supplies product information and pricing to the Order Service through REST APIs.

The Order Service uses this information when creating an order and calculating the order total.

The Product Service remains independent from the asynchronous order-processing workflow handled by Apache Kafka.

The overall event-driven workflow is handled by the respective services:

~~~text
OrderCreated
     │
     ▼
InventoryReserved
     │
     ▼
PaymentSucceeded
     │
     ▼
ShipmentCreated
     │
     ▼
Notification
~~~

---

## Version

Current Version: **v2.0.0**