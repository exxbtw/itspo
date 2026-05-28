import grpc
from concurrent import futures
import time

import notifications_pb2
import notifications_pb2_grpc

# Shared in-memory storage (same process as FastAPI)
notifications_db: dict = {}
notifications_counter: int = 0


class NotificationsServicer(notifications_pb2_grpc.NotificationsServiceServicer):

    def CreateNotification(self, request, context):
        global notifications_counter
        notifications_counter += 1
        nid = notifications_counter
        item = {
            "id": nid,
            "title": request.title,
            "message": request.message,
            "channel": request.channel,
        }
        notifications_db[nid] = item
        return notifications_pb2.CreateNotificationResponse(
            id=nid,
            title=item["title"],
            message=item["message"],
            channel=item["channel"],
        )

    def ListNotifications(self, request, context):
        items = [
            notifications_pb2.NotificationItem(
                id=v["id"], title=v["title"], message=v["message"], channel=v["channel"]
            )
            for v in notifications_db.values()
        ]
        return notifications_pb2.ListNotificationsResponse(notifications=items)


def serve_grpc():
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    notifications_pb2_grpc.add_NotificationsServiceServicer_to_server(
        NotificationsServicer(), server
    )
    server.add_insecure_port("[::]:50051")
    print("gRPC server running on port 50051...")
    server.start()
    try:
        while True:
            time.sleep(86400)
    except KeyboardInterrupt:
        server.stop(0)


if __name__ == "__main__":
    serve_grpc()
