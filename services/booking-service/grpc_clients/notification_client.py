import os
import grpc
from grpc_clients.protos import notification_pb2, notification_pb2_grpc

NOTIFICATION_SERVICE_HOST = os.getenv("NOTIFICATION_SERVICE_HOST", "localhost:50051")

class NotificationClient:
    def __init__(self):
        self.channel = grpc.insecure_channel(NOTIFICATION_SERVICE_HOST)
        self.stub = notification_pb2_grpc.NotificationServiceStub(self.channel)

    def send_notification(self, user_id: str, type: str, title: str, message: str, data: str = ""):
        request = notification_pb2.SendNotificationRequest(
            user_id=str(user_id),
            type=type,
            title=title,
            message=message,
            data=data
        )
        try:
            response = self.stub.SendNotification(request)
            return response.success, response.notification_id
        except grpc.RpcError as e:
            print(f"Failed to send notification via gRPC: {e}")
            return False, ""

notification_client = NotificationClient()
