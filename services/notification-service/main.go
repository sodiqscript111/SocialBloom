package main

import (
	"log"
	"net"
	"os"
	"os/signal"
	"syscall"

	"github.com/sodiqscript111/socialbloom/notification-service/db"
	pb "github.com/sodiqscript111/socialbloom/notification-service/pb"
	"github.com/sodiqscript111/socialbloom/notification-service/server"
	"google.golang.org/grpc"
	"google.golang.org/grpc/reflection"
)

func main() {
	db.InitDB()

	port := os.Getenv("PORT")
	if port == "" {
		port = "50051"
	}

	lis, err := net.Listen("tcp", ":"+port)
	if err != nil {
		log.Fatalf("Failed to listen: %v", err)
	}

	grpcServer := grpc.NewServer()
	pb.RegisterNotificationServiceServer(grpcServer, &server.NotificationServer{})
	
	// Register reflection service on gRPC server. (useful for grpcurl)
	reflection.Register(grpcServer)

	log.Printf("Notification gRPC service listening on port %s...", port)
	
	go func() {
		if err := grpcServer.Serve(lis); err != nil {
			log.Fatalf("Failed to serve: %v", err)
		}
	}()

	quit := make(chan os.Signal, 1)
	signal.Notify(quit, syscall.SIGINT, syscall.SIGTERM)
	<-quit

	log.Println("Shutting down gracefully...")
	grpcServer.GracefulStop()
	log.Println("Server stopped")
}
