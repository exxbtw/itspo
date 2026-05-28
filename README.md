# notifications-s11

Финальный проект. Распределённый сервис уведомлений с REST API и gRPC.

## Запуск

```bash
docker compose up --build
```

## Проверка

```bash
# Создать уведомление
curl -X POST http://localhost:8080/api/notifications \
  -H "Content-Type: application/json" \
  -d '{"title": "Hello", "message": "Test", "channel": "email"}'

# Получить список
curl http://localhost:8080/api/notifications

# Health check
curl http://localhost:8080/health
```

## Структура

```
week-17/
├── ARCHITECTURE.md
├── README.md
├── docker-compose.yml
├── notifications-svc/
│   ├── main.py                # FastAPI REST
│   ├── grpc_server.py         # gRPC сервер
│   ├── proto/
│   │   └── notifications.proto
│   ├── requirements.txt
│   └── Dockerfile
├── sender-svc/
│   ├── main.py                # gRPC сервер отправки
│   ├── requirements.txt
│   └── Dockerfile
├── infra/
│   └── nginx.conf             # Gateway
├── k8s/
│   ├── deployment.yaml
│   └── service.yaml
└── .github/
    └── workflows/
        └── ci.yml
```

## Kubernetes

```bash
kubectl apply -f k8s/
```

Настроен RollingUpdate с двумя репликами — zero downtime при обновлении.

## CI/CD

GitHub Actions — `.github/workflows/ci.yml`

Запускается на push/PR в `main`: lint → build → deploy (kubectl apply).