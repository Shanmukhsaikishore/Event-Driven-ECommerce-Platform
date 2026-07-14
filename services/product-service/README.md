# Product Service

## Overview

The Product Service is responsible for managing the product catalog in the Event-Driven E-Commerce Platform.

It provides REST APIs for creating, retrieving, updating, and deleting products. Since product browsing is a read-heavy operation and does not require asynchronous communication, this service communicates synchronously using HTTP APIs in Version 1.

---

## Business Responsibility

The Product Service is responsible for:

- Managing product information
- Creating new products
- Updating product details
- Deleting products
- Retrieving product catalog
- Providing product information to other services through REST APIs

This service **does not** manage inventory, orders, payments, or shipments.

---

## Why Product Service Does Not Use Kafka

Kafka is used when business events need to be shared asynchronously between multiple independent services.

In Version 1:

- Product browsing is synchronous.
- Other services query product information directly through REST APIs.
- Product updates do not currently require event propagation.

Kafka integration can be introduced in future versions if product updates need to notify other services.

---

## Architecture

```
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
```

---

## Project Structure

```
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
```

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

---

## How to Run

Start PostgreSQL:

```bash
docker compose up -d
```

Activate virtual environment:

```bash
.venv\Scripts\activate
```

Install dependencies:

```bash
uv sync
```

Run the service:

```bash
uv run uvicorn app.main:app --reload
```

Swagger UI:

```
http://localhost:8000/docs
```

---

## Design Decisions

- Layered Architecture
- Repository Pattern
- Service Layer
- Environment-based Configuration
- SQLAlchemy ORM
- RESTful API Design
- PostgreSQL as the source of truth



---

## Role in Event-Driven E-Commerce Platform

The Product Service owns the product catalog.

It supplies product information to the Order Service through REST APIs.

Business events such as Order Created, Payment Completed, Inventory Updated, Shipment Created, and Notification Sent are handled by other services through Apache Kafka.

---

## Version

Current Version: **v1.0.0**