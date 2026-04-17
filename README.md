# Kanban Project Management Tool

A full-stack real-time Kanban board built with:

- **Backend**: FastAPI + PostgreSQL + Redis + WebSockets
- **Frontend**: React + Next.js + Tailwind CSS
- **DevOps**: Docker + GitHub Actions CI/CD

## Tech Stack

| Layer    | Technology                    |
| -------- | ----------------------------- |
| API      | FastAPI (Python)              |
| Database | PostgreSQL + SQLAlchemy ORM   |
| Cache    | Redis (WebSocket Pub/Sub)     |
| Frontend | Next.js + Tailwind CSS        |
| Auth     | JWT (access + refresh tokens) |
| DevOps   | Docker + GitHub Actions       |

## Features

- JWT Authentication (register / login)
- Create boards, columns, and cards
- Drag and drop cards across columns
- Real-time sync across tabs via WebSockets
- CI/CD pipeline with GitHub Actions

## Run locally

### Prerequisites

- Docker and Docker Compose installed

### Steps

1. Clone the repo
   git clone https://github.com/YOUR_USERNAME/kanban-project-management.git
   cd kanban-project-management

2. Create your .env file (copy from .env.example and fill values)
   cp .env.example .env

3. Start all services
   docker-compose up --build

- Frontend: http://localhost:3000
- API: http://localhost:8000
- API Docs: http://localhost:8000/docs

## Project Structure

backend/ FastAPI app, models, services, websockets
frontend/ Next.js app, components, store, hooks
