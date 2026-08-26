package db

import (
	"log"
	"os"

	"github.com/sodiqscript111/socialbloom/notification-service/models"
	"gorm.io/driver/postgres"
	"gorm.io/gorm"
)

var DB *gorm.DB

func InitDB() {
	dsn := os.Getenv("DATABASE_URL")
	if dsn == "" {
		dsn = "host=postgres user=postgres password=password dbname=notificationsdb port=5432 sslmode=disable"
	} else {
		// Strip postgresql+psycopg:// and replace with postgres:// for GORM compatibility if needed
		// Actually, GORM postgres driver expects standard postgres:// or DSN format.
		// If python used postgresql+psycopg://, let's just use the DSN.
	}
	
	// Quick hack to convert sqlalchemy url to standard postgres url
	if len(dsn) > 19 && dsn[:19] == "postgresql+psycopg:" {
		dsn = "postgres:" + dsn[19:]
	}

	var err error
	DB, err = gorm.Open(postgres.Open(dsn), &gorm.Config{})
	if err != nil {
		log.Fatalf("Failed to connect to database: %v", err)
	}

	err = DB.AutoMigrate(&models.Notification{})
	if err != nil {
		log.Fatalf("Failed to auto-migrate: %v", err)
	}
}
