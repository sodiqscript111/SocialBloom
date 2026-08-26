package models

import (
	"time"
)

type Notification struct {
	ID        string    `gorm:"type:uuid;primaryKey"`
	UserID    string    `gorm:"index;not null"`
	Type      string    `gorm:"not null"`
	Title     string    `gorm:"not null"`
	Message   string    `gorm:"not null"`
	Data      string
	IsRead    bool      `gorm:"default:false"`
	CreatedAt time.Time `gorm:"autoCreateTime"`
}
