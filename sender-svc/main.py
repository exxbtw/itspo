import grpc
from concurrent import futures
import time
import logging

import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

import notifications_pb2
import notifications_pb2_grpc

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [sender-svc] %(levelname)s: %(message)s"
)
logger = logging.getLogger(__name__)


class SenderServicer(notifications_pb2_grpc.NotificationsServiceServicer):

    def CreateNotification(self, request, context):
        logger.info(
            f"Отправка уведомления | channel={request.channel} "
            f"title='{request.title}' message='{request.message}'"
        )

        # Имитация отправки по каналу
        if request.channel == "email":
            logger.info(f"[EMAIL] Отправлено: {request.title}")
        elif request.channel == "sms":
            logger.info(f"[SMS] Отправлено: {request.message}")
        else:
            logger.info(f"[PUSH] Отправлено: {request.title}")

        return notifications_pb2.CreateNotificationResponse(
            id=1,
            title=request.title,
            message=request.message,
            channel=request.channel,
        )

    def ListNotifications(self, request, context):
        return notifications_pb2.ListNotificationsResponse(notifications=[])


def serve():
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    notifications_pb2_grpc.add_NotificationsServiceServicer_to_server(
        SenderServicer(), server
    )
    server.add_insecure_port("[::]:50052")
    logger.info("sender-svc gRPC запущен на порту 50052")
    server.start()
    try:
        while True:
            time.sleep(86400)
    except KeyboardInterrupt:
        server.stop(0)


if __name__ == "__main__":
    serve()
