# 🛠️ Technologies Used


The project was developed using modern tools and technologies, divided into categories:

---

## 🧠 Backend
- **FastAPI** - modern web framework for creating fast APIs.
- **SQLAlchemy (async)** - asynchronous ORM for working with database.
- **Alembic** - a tool for managing database migrations.
- **RabbitMQ** - message broker for asynchronous task processing.
- **Poetry** - dependency manager and project builder.
- **Git** - version control system.

---

## 🗄️ Database
- **PostgreSQL** is the main relational database.
- **Neon** - PostgreSQL cloud provider with support for serverless features and branching.
  
---

## ☁️ Infrastructure & DevOps
- **S3** - storage for files and images (e.g. AWS S3 or compatible counterparts).
- **Nginx** - reverse proxy server for request routing and static distribution.
- **Docker** - containerizing an application for easy deployment and isolation of the environment



---

##

#### Examples API

## 👤 Users

### 🔹 Create user

- **POST** `/api/users/create`

**The body of the request (JSON):**

```json
{
  "name": "Casper",
  "email": "casper@example.com",
  "password": "supersecure"
}
```

---

## 🍽️Restaurants 
### 🔹 Create restaurant
- **POST** `/api/restaurants/create`
**The body of the request (JSON):**

```json
{
  "main_image": "image",
  "images": "list[images]",
  "name": "Япіко",
  "description": "Ресторан з японською кухнею",
  "menu": "Суші супи напої",
  "comments": "дуже смачна їжа",
  "detailed_description": "детальний опис"
}
```
### 🔹 Get restaurant
- **GET** `/api/restaurants/{pk}`
```json
{
  "id": 0,
  "name": "string",
  "description": "string",
  "menu": "string",
  "comments": "string",
  "detailed_description": "string",
  "main_image": "string",
  "images": ["string"]
}
```

### 🔹 Get restaurant
- **GET** `/api/restaurants/`
```json
{
  "q": "string",
  "page": "int",
  "limit": "int",
  "order_direction": "asc/desc",
  "sort_by": "id/price",
  "use_sharp_q_filter": "True/False"
}
```


## 🔐Auth
### 🔹 User Login
- **POST** `api/auth/login`
```json
{
  "username": "string",
  "password": "string"
}
```

### 🔹Get user's info
- **GET** `api/auth/get_my_info`
```json
{
  "email": "example@gmail.com",
  "name": "string",
  "id": "int"
}
```

