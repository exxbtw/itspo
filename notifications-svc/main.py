import logging
import threading
import grpc

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List

import notifications_pb2
import notifications_pb2_grpc
from grpc_server import serve_grpc, notifications_db, notifications_counter

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [notifications-svc] %(levelname)s: %(message)s"
)
logger = logging.getLogger(__name__)

app = FastAPI(title="notifications-svc-s11")


class NotificationIn(BaseModel):
    title: str
    message: str
    channel: str


class NotificationOut(BaseModel):
    id: int
    title: str
    message: str
    channel: str


def call_sender(title: str, message: str, channel: str):
    """Вызываем sender-svc через gRPC для отправки уведомления."""
    try:
        channel_grpc = grpc.insecure_channel("sender-svc:50052")
        stub = notifications_pb2_grpc.NotificationsServiceStub(channel_grpc)
        stub.CreateNotification(
            notifications_pb2.CreateNotificationRequest(
                title=title, message=message, channel=channel
            ),
            timeout=3,
        )
        logger.info(f"sender-svc вызван успешно | channel={channel}")
    except Exception as e:
        logger.warning(f"sender-svc недоступен (не критично): {e}")


@app.get("/notifications", response_model=List[NotificationOut])
def get_notifications():
    logger.info(f"GET /notifications — записей: {len(notifications_db)}")
    return list(notifications_db.values())


@app.post("/notifications", response_model=NotificationOut, status_code=201)
def create_notification(body: NotificationIn):
    import grpc_server
    grpc_server.notifications_counter += 1
    nid = grpc_server.notifications_counter
    item = {"id": nid, "title": body.title, "message": body.message, "channel": body.channel}
    grpc_server.notifications_db[nid] = item
    logger.info(f"POST /notifications | id={nid} channel={body.channel} title='{body.title}'")

    # Асинхронно вызываем sender-svc через gRPC
    t = threading.Thread(target=call_sender, args=(body.title, body.message, body.channel), daemon=True)
    t.start()

    return item


@app.get("/notifications/{notification_id}", response_model=NotificationOut)
def get_notification(notification_id: int):
    item = notifications_db.get(notification_id)
    if not item:
        logger.warning(f"GET /notifications/{notification_id} — не найдено")
        raise HTTPException(status_code=404, detail="Notification not found")
    return item


@app.get("/health")
def health():
    return {"status": "ok", "service": "notifications-svc-s11"}


@app.on_event("startup")
def startup_grpc():
    logger.info("Запуск notifications-svc-s11...")
    t = threading.Thread(target=serve_grpc, daemon=True)
    t.start()
    logger.info("gRPC сервер запущен на порту 50051")
