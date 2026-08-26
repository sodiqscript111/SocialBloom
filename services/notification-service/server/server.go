package server

import (
	"context"
	"time"

	"github.com/google/uuid"
	"github.com/sodiqscript111/socialbloom/notification-service/db"
	"github.com/sodiqscript111/socialbloom/notification-service/models"
	pb "github.com/sodiqscript111/socialbloom/notification-service/pb"
	"google.golang.org/grpc/codes"
	"google.golang.org/grpc/status"
	"google.golang.org/protobuf/types/known/timestamppb"
)

type NotificationServer struct {
	pb.UnimplementedNotificationServiceServer
}

func (s *NotificationServer) SendNotification(ctx context.Context, req *pb.SendNotificationRequest) (*pb.NotificationResponse, error) {
	notif := models.Notification{
		ID:      uuid.New().String(),
		UserID:  req.UserId,
		Type:    req.Type,
		Title:   req.Title,
		Message: req.Message,
		Data:    req.Data,
	}

	if err := db.DB.Create(&notif).Error; err != nil {
		return nil, status.Errorf(codes.Internal, "Failed to create notification: %v", err)
	}

	return &pb.NotificationResponse{
		Success:        true,
		NotificationId: notif.ID,
	}, nil
}

func (s *NotificationServer) GetNotifications(ctx context.Context, req *pb.GetNotificationsRequest) (*pb.GetNotificationsResponse, error) {
	var notifs []models.Notification
	var total int64

	query := db.DB.Model(&models.Notification{}).Where("user_id = ?", req.UserId)

	if req.UnreadOnly {
		query = query.Where("is_read = ?", false)
	}

	query.Count(&total)

	if req.Limit > 0 {
		query = query.Limit(int(req.Limit))
	}
	if req.Offset > 0 {
		query = query.Offset(int(req.Offset))
	}

	if err := query.Order("created_at desc").Find(&notifs).Error; err != nil {
		return nil, status.Errorf(codes.Internal, "Failed to fetch notifications: %v", err)
	}

	var pbNotifs []*pb.NotificationMessage
	for _, n := range notifs {
		pbNotifs = append(pbNotifs, &pb.NotificationMessage{
			Id:        n.ID,
			UserId:    n.UserID,
			Type:      n.Type,
			Title:     n.Title,
			Message:   n.Message,
			Data:      n.Data,
			IsRead:    n.IsRead,
			CreatedAt: timestamppb.New(n.CreatedAt),
		})
	}

	return &pb.GetNotificationsResponse{
		Notifications: pbNotifs,
		TotalCount:    int32(total),
	}, nil
}

func (s *NotificationServer) StreamNotifications(req *pb.StreamNotificationsRequest, stream pb.NotificationService_StreamNotificationsServer) error {
	lastCheck := time.Now().UTC()

	for {
		// A simple simulated streaming heartbeat
		select {
		case <-stream.Context().Done():
			return nil
		default:
		}

		var newNotifs []models.Notification
		err := db.DB.Where("user_id = ? AND created_at > ?", req.UserId, lastCheck).Order("created_at asc").Find(&newNotifs).Error
		
		if err == nil {
			for _, n := range newNotifs {
				msg := &pb.NotificationMessage{
					Id:        n.ID,
					UserId:    n.UserID,
					Type:      n.Type,
					Title:     n.Title,
					Message:   n.Message,
					Data:      n.Data,
					IsRead:    n.IsRead,
					CreatedAt: timestamppb.New(n.CreatedAt),
				}
				if err := stream.Send(msg); err != nil {
					return err
				}
				lastCheck = n.CreatedAt
			}
		}

		time.Sleep(2 * time.Second)
	}
}

func (s *NotificationServer) MarkAsRead(ctx context.Context, req *pb.MarkAsReadRequest) (*pb.MarkAsReadResponse, error) {
	var notif models.Notification
	if err := db.DB.Where("id = ? AND user_id = ?", req.NotificationId, req.UserId).First(&notif).Error; err != nil {
		return nil, status.Errorf(codes.NotFound, "Notification not found")
	}

	notif.IsRead = true
	if err := db.DB.Save(&notif).Error; err != nil {
		return nil, status.Errorf(codes.Internal, "Failed to update notification: %v", err)
	}

	return &pb.MarkAsReadResponse{Success: true}, nil
}
