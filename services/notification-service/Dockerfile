FROM golang:1.21-bullseye AS builder

WORKDIR /app

# Install protoc and go plugins
RUN apt-get update && apt-get install -y protobuf-compiler && \
    go install google.golang.org/protobuf/cmd/protoc-gen-go@latest && \
    go install google.golang.org/grpc/cmd/protoc-gen-go-grpc@latest

# Add go bin to path
ENV PATH="$PATH:$(go env GOPATH)/bin"

# Download dependencies
COPY go.mod go.sum ./
RUN go mod download

# Copy source code
COPY . .

# Generate protos
RUN mkdir -p pb && \
    protoc --go_out=pb --go_opt=paths=source_relative \
           --go-grpc_out=pb --go-grpc_opt=paths=source_relative \
           -Iprotos protos/notification.proto

# Build binary
RUN CGO_ENABLED=0 GOOS=linux go build -o notification-service main.go

# Stage 2: Minimal runtime image
FROM debian:bullseye-slim

WORKDIR /app

COPY --from=builder /app/notification-service .

EXPOSE 50051

CMD ["./notification-service"]
