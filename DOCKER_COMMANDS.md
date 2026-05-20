# 🐳 Docker Commands — Enterprise RAG Platform

## ▶️ Start All Services

```powershell
# From the enterprise-rag-platform directory
cd d:\RAG-production-pipeline\enterprise-rag-platform

# Build and start all services (foreground)

docker-compose up --build
# Build and start all services (background / detached)
docker-compose up --build -d
```

---

## 🎯 Run Individual Services

```powershell
# Backend API only
docker-compose up --build backend

# Frontend only
docker-compose up --build frontend

# Infrastructure (Redis + RabbitMQ) only
docker-compose up redis rabbitmq

# Background worker only
docker-compose up --build worker

# Observability stack (Prometheus + Grafana)
docker-compose up prometheus grafana
```

---

## 📌 Service Port Map

| Service            | URL                        |
|--------------------|----------------------------|
| Backend API        | http://localhost:8000       |
| Frontend           | http://localhost:3002       |
| Redis Stack UI     | http://localhost:8001       |
| RabbitMQ Mgmt UI   | http://localhost:15672      |
| Prometheus         | http://localhost:9090       |
| Grafana            | http://localhost:3001       |

---

## 🔍 Inspect & Debug

```powershell
# View running containers
docker-compose ps

# Stream logs from all services
docker-compose logs -f

# Stream logs from a specific service
docker-compose logs -f backend
docker-compose logs -f worker
docker-compose logs -f frontend

# Open a shell inside the backend container
docker-compose exec backend bash

# Open a shell inside the worker container
docker-compose exec worker bash
```

---

## 🔄 Rebuild & Restart

```powershell
# Rebuild a specific service without cache
docker-compose build --no-cache backend

# Restart a specific service
docker-compose restart backend

# Pull latest base images
docker-compose pull
```

---

## 🛑 Stop & Cleanup

```powershell
# Stop all running containers (keep volumes)
docker-compose down

# Stop and remove volumes (wipes Redis + RabbitMQ data)
docker-compose down -v

# Stop and remove everything including images
docker-compose down --rmi all -v
```

---

## ⚠️ Prerequisites

- Ensure `.env` is populated at `enterprise-rag-platform/.env` before running.  
  Copy from the example if needed:
  ```powershell
  cp .env.example .env
  ```
- Docker Desktop must be running.
- Minimum recommended: **8 GB RAM** allocated to Docker.
