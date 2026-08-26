import os
import grpc
import json
import logging
import os
import sys
sys.path.append(os.path.join(os.path.dirname(__file__), 'protos'))
from grpc_clients.protos import notification_pb2, notification_pb2_grpc

logger = logging.getLogger(__name__)

NOTIFICATION_SERVICE_HOST = os.getenv("NOTIFICATION_SERVICE_HOST", "localhost:50051")

class NotificationClient:
    def __init__(self):
        self.channel = grpc.insecure_channel(NOTIFICATION_SERVICE_HOST)
        self.stub = notification_pb2_grpc.NotificationServiceStub(self.channel)

    def send_notification(self, user_id: str, type: str, title: str, message: str, data: str = "") -> tuple[bool, str]:
        request = notification_pb2.SendNotificationRequest(
            user_id=str(user_id),
            type=type,
            title=title,
            message=message,
            data=data
        )
        try:
            # 5 second timeout to prevent cascading failures
            response = self.stub.SendNotification(request, timeout=5.0)
            return response.success, response.notification_id
        except grpc.RpcError as e:
            logger.error(f"Failed to send notification via gRPC: {e.details()} (code: {e.code()})")
            return False, ""

notification_client = NotificationClient()

def notify(user_id: int, notif_type: str, title: str, message: str, **data) -> tuple[bool, str]:
    """Helper method to standardize notification sending with JSON serialization"""
    return notification_client.send_notification(
        user_id=str(user_id),
        type=notif_type,
        title=title,
        message=message,
        data=json.dumps(data) if data else ""
    )
