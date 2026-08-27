package server_test

import (
	"context"
	"os"
	"testing"
	"time"

	"github.com/google/uuid"
	"github.com/stretchr/testify/assert"
	"github.com/stretchr/testify/require"
	"github.com/testcontainers/testcontainers-go"
	"github.com/testcontainers/testcontainers-go/modules/postgres"
	"github.com/testcontainers/testcontainers-go/wait"
	pgdriver "gorm.io/driver/postgres"
	"gorm.io/gorm"

	"github.com/sodiqscript111/socialbloom/notification-service/db"
	"github.com/sodiqscript111/socialbloom/notification-service/models"
	pb "github.com/sodiqscript111/socialbloom/notification-service/pb"
	"github.com/sodiqscript111/socialbloom/notification-service/server"
)

var testServer *server.NotificationServer

func TestMain(m *testing.M) {
	ctx := context.Background()

	// 1. Spin up a PostgreSQL Testcontainer
	postgresContainer, err := postgres.Run(ctx,
		"postgres:15-alpine",
		postgres.WithDatabase("testdb"),
		postgres.WithUsername("postgres"),
		postgres.WithPassword("password"),
		testcontainers.WithWaitStrategy(
			wait.ForLog("database system is ready to accept connections").
				WithOccurrence(2).WithStartupTimeout(5*time.Second)),
	)
	if err != nil {
		panic(err)
	}

	// Clean up container after tests finish
	defer func() {
		if err := postgresContainer.Terminate(ctx); err != nil {
			panic(err)
		}
	}()

	// 2. Get connection string and connect
	connStr, err := postgresContainer.ConnectionString(ctx, "sslmode=disable")
	if err != nil {
		panic(err)
	}

	testDB, err := gorm.Open(pgdriver.Open(connStr), &gorm.Config{})
	if err != nil {
		panic(err)
	}

	// 3. Migrate database and inject into global db package
	err = testDB.AutoMigrate(&models.Notification{})
	if err != nil {
		panic(err)
	}
	db.DB = testDB

	// 4. Init server
	testServer = &server.NotificationServer{}

	// 5. Run tests
	code := m.Run()
	os.Exit(code)
}

func TestSendNotification(t *testing.T) {
	ctx := context.Background()

	req := &pb.SendNotificationRequest{
		UserId:  "user-123",
		Type:    "EMAIL",
		Title:   "Welcome!",
		Message: "Hello from testcontainers",
		Data:    "{}",
	}

	res, err := testServer.SendNotification(ctx, req)
	
	require.NoError(t, err)
	assert.True(t, res.Success)
	assert.NotEmpty(t, res.NotificationId)

	// Verify in DB
	var notif models.Notification
	err = db.DB.Where("id = ?", res.NotificationId).First(&notif).Error
	require.NoError(t, err)
	assert.Equal(t, "user-123", notif.UserID)
	assert.Equal(t, "Welcome!", notif.Title)
}

func TestGetNotifications(t *testing.T) {
	ctx := context.Background()

	notifID1 := uuid.New().String()
	notifID2 := uuid.New().String()

	// Seed data
	db.DB.Create(&models.Notification{
		ID:      notifID1,
		UserID:  "user-456",
		Title:   "First",
		IsRead:  false,
	})
	db.DB.Create(&models.Notification{
		ID:      notifID2,
		UserID:  "user-456",
		Title:   "Second",
		IsRead:  true,
	})

	// Test getting all
	req := &pb.GetNotificationsRequest{
		UserId: "user-456",
	}
	res, err := testServer.GetNotifications(ctx, req)
	
	require.NoError(t, err)
	assert.Equal(t, int32(2), res.TotalCount)
	assert.Len(t, res.Notifications, 2)

	// Test unread only
	reqUnread := &pb.GetNotificationsRequest{
		UserId:     "user-456",
		UnreadOnly: true,
	}
	resUnread, err := testServer.GetNotifications(ctx, reqUnread)
	
	require.NoError(t, err)
	assert.Equal(t, int32(1), resUnread.TotalCount)
	assert.Len(t, resUnread.Notifications, 1)
	assert.Equal(t, "First", resUnread.Notifications[0].Title)
}

func TestMarkAsRead(t *testing.T) {
	ctx := context.Background()
	
	notifID3 := uuid.New().String()

	// Seed data
	db.DB.Create(&models.Notification{
		ID:      notifID3,
		UserID:  "user-789",
		Title:   "Read Me",
		IsRead:  false,
	})

	req := &pb.MarkAsReadRequest{
		UserId:         "user-789",
		NotificationId: notifID3,
	}

	res, err := testServer.MarkAsRead(ctx, req)
	require.NoError(t, err)
	assert.True(t, res.Success)

	// Verify in DB
	var notif models.Notification
	err = db.DB.Where("id = ?", notifID3).First(&notif).Error
	require.NoError(t, err)
	assert.True(t, notif.IsRead)
}
