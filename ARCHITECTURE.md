# Architecture — notifications-s11

## Project Code
notifications-s11

## Суть

Распределённый сервис уведомлений. Система принимает уведомления через REST API, сохраняет их и асинхронно отправляет по нужному каналу (email, sms, push) через 2 сервис.
Система состоит из трёх компонентов: nginx-шлюз, основной сервис уведомлений и сервис отправки.

## Как это работает

Клиент отправляет запрос на порт 8080 (nginx), который работает как API-шлюз. Он принимает запросы на /api/notifications и проксирует их в notifications-svc-s11 на порт 8131. Когда создаётся новое уведомление, notifications-svc асинхронно вызывает sender-svc через gRPC и тот получает задачу и "отправляет" по нужному каналу.

## Компоненты

### api-gateway
nginx reverse proxy на порту 8080, этоточка входа для клиентов. Маршрут /api/notifications проксируется в notifications-svc-s11:8131.

### notifications-svc-s11
Основной сервис на FastAPI, порт 8131. Реализует REST API для управления уведомлениями. Данные хранит в памяти. После создания уведомления асинхронно вызывает sender-svc через gRPC. Также поднимает собственный gRPC сервер на порту 50051. Логирует все входящие запросы.

### sender-svc
Сервис отправки на порту 50052, реализован как чистый gRPC сервер. Полусает задачу от notifications-svc и имитирует отправку по каналу: email, sms или push. Логирует каждую отправку.

## Протоколы

REST используется для внешнего взаимодействия: клиент обращается к gateway, gateway проксирует в notifications-svc.
gRPC используется для внутреннего взаимодействия между сервисами: notifications-svc вызывает sender-svc.

## REST API

| Метод | Путь | Описание |
|-------|------|----------|
|  GET  | /api/notifications | Список уведомлений |
|  POST | /api/notifications | Создать уведомление |
|  GET  | /api/notifications/{id} | Получить по ID |
|  GET  | /health | Проверка работоспособности |

Пример запроса:
```json
POST /api/notifications
{
  "title": "Hello",
  "message": "Test notification",
  "channel": "email"
}
```

## gRPC API

Пакет notifications.v1, сервис NotificationsService.

Методы: CreateNotification и ListNotifications. Контракт описан в notifications-svc/proto/notifications.proto. Тот же proto-файл используется в обоих сервисах.

## Логирование

Оба сервиса пишут логи в формате:
```
2026-05-27 15:01:37 [notifications-svc] INFO: POST /notifications | id=1 channel=email title='Hello'
2026-05-27 15:01:37 [sender-svc] INFO: [EMAIL] Отправлено: Hello
```
Посмотреть можно в docker compose logs -f

## Запуск

```bash
docker compose up --build
```

## Kubernetes

Манифесты в k8s/. Deployment notifications-app с контейнером notifications-container, Service notifications-svc-s11 на портах 8131 и 50051. Настроена стратегия RollingUpdate с двумя репликами — при обновлении K8s поднимает новый под раньше чем гасит старый, сервис остаётся доступным.

```bash
kubectl apply -f k8s/
```

## CI/CD

GitHub Actions, файл .github/workflows/ci.yml. Запускается на push и pull request в main. Два job-а: build (lint через flake8, сборка Docker образа) и deploy (kubectl apply -f k8s/, запускается только при push в main после успешного build).

