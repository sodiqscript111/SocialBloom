import os
import sys
import time
import grpc
from concurrent import futures
import json
from datetime import datetime
from google.protobuf.timestamp_pb2 import Timestamp

# Add current directory to path to find generated protos
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from protos import notification_pb2
from protos import notification_pb2_grpc
from db import SessionLocal, engine, Base
from models import Notification

class NotificationServicer(notification_pb2_grpc.NotificationServiceServicer):
    
    def SendNotification(self, request, context):
        db = SessionLocal()
        try:
            new_notif = Notification(
                user_id=request.user_id,
                type=request.type,
                title=request.title,
                message=request.message,
                data=request.data
            )
            db.add(new_notif)
            db.commit()
            db.refresh(new_notif)
            return notification_pb2.NotificationResponse(
                success=True,
                notification_id=new_notif.id
            )
        except Exception as e:
            db.rollback()
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details(str(e))
            return notification_pb2.NotificationResponse(success=False, notification_id="")
        finally:
            db.close()

    def GetNotifications(self, request, context):
        db = SessionLocal()
        try:
            query = db.query(Notification).filter(Notification.user_id == request.user_id)
            if request.unread_only:
                query = query.filter(Notification.is_read == False)
            
            total = query.count()
            
            # Apply limit/offset if provided
            if request.limit > 0:
                query = query.limit(request.limit)
            if request.offset > 0:
                query = query.offset(request.offset)
                
            notifs = query.order_by(Notification.created_at.desc()).all()
            
            response_notifs = []
            for n in notifs:
                ts = Timestamp()
                ts.FromDatetime(n.created_at)
                msg = notification_pb2.NotificationMessage(
                    id=n.id,
                    user_id=n.user_id,
                    type=n.type,
                    title=n.title,
                    message=n.message,
                    data=n.data or "",
                    is_read=n.is_read,
                    created_at=ts
                )
                response_notifs.append(msg)
                
            return notification_pb2.GetNotificationsResponse(
                notifications=response_notifs,
                total_count=total
            )
        finally:
            db.close()

    def StreamNotifications(self, request, context):
        # A simple simulated streaming of notifications. 
        # In a real app, this would tie into a pubsub or Redis stream.
        # For Istio streaming practice, we stream a heartbeat and any new db notifications.
        last_check = datetime.utcnow()
        while context.is_active():
            db = SessionLocal()
            try:
                new_notifs = db.query(Notification).filter(
                    Notification.user_id == request.user_id,
                    Notification.created_at > last_check
                ).order_by(Notification.created_at.asc()).all()
                
                for n in new_notifs:
                    ts = Timestamp()
                    ts.FromDatetime(n.created_at)
                    msg = notification_pb2.NotificationMessage(
                        id=n.id,
                        user_id=n.user_id,
                        type=n.type,
                        title=n.title,
                        message=n.message,
                        data=n.data or "",
                        is_read=n.is_read,
                        created_at=ts
                    )
                    context.write(msg)
                    last_check = n.created_at
            finally:
                db.close()
            time.sleep(2) # poll every 2 seconds

    def MarkAsRead(self, request, context):
        db = SessionLocal()
        try:
            notif = db.query(Notification).filter(
                Notification.id == request.notification_id,
                Notification.user_id == request.user_id
            ).first()
            if notif:
                notif.is_read = True
                db.commit()
                return notification_pb2.MarkAsReadResponse(success=True)
            else:
                context.set_code(grpc.StatusCode.NOT_FOUND)
                context.set_details("Notification not found")
                return notification_pb2.MarkAsReadResponse(success=False)
        finally:
            db.close()

def serve():
    Base.metadata.create_all(bind=engine)
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    notification_pb2_grpc.add_NotificationServiceServicer_to_server(NotificationServicer(), server)
    port = os.getenv("PORT", "50051")
    server.add_insecure_port(f'[::]:{port}')
    server.start()
    print(f"Notification gRPC service listening on port {port}...")
    server.wait_for_termination()

if __name__ == '__main__':
    serve()
