# 🍽️ Restaurant Menu App

A small full-stack project where **customers** can create an account and view the menu, and **managers** can add, edit or delete dishes. The app is containerized (frontend, backend, PostgreSQL) so it’s easy to run locally or deploy.

---

## Features

- 🔐 User registration & login (JWT)
- 👤 Two roles: **Customer** and **Manager**
- 📋 Customers: view menu (starters, main courses, desserts)
- 🧑‍💼 Managers: add / update / delete dishes
- 🐳 Dockerized (backend, frontend, PostgreSQL)

---

## Tech Stack

- Frontend: React + Axios  
- Backend: Flask + SQLAlchemy + Flask-JWT-Extended  
- Database: PostgreSQL  
- Containerization: Docker & Docker Compose

---

## Project Structure

```
RestaurantMenuProject/
├── app.py
├── models.py
├── import_data.py
├── requirements.txt
├── Dockerfile
├── docker-compose.yml
├── frontend/
│ ├── src/
│ └── Dockerfile
└── restaurant_menu_refined.csv
```

---

## 🐳 Run with Docker

Make sure Docker Desktop is running, then execute:

```bash
docker-compose up --build
```

---

## API Endpoints


| Method  | Endpoint                  | Description                          | Access         |
|---------|---------------------------|--------------------------------------|----------------|
| `POST`  | `/register`               | Register a new user                  | Public         |
| `POST`  | `/login`                  | Log in → returns a **JWT token**     | Public         |
| `GET`   | `/menu`                   | Fetch all menu items                 | Public / Auth  |
| `POST`  | `/add_dish`               | Add a new dish                       | **Manager**    |
| `PUT`   | `/update_dish/<id>`       | Update an existing dish              | **Manager**    |
| `DELETE`| `/delete_dish/<id>`       | Delete a dish                        | **Manager**    |

> **Note**: The `add_dish`, `update_dish`, and `delete_dish` routes require **Manager role** and a valid **JWT token** in the header:
> ```
> Authorization: Bearer <jwt_token>
> ```

--- 

## Author
### Ahmed Mnaouer
📊 Data Science & Business Analytics Enthusiast

[Linkedin](https://www.linkedin.com/in/ahmedmnaouer/)
