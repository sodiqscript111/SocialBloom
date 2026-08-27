#!/bin/bash

echo "Building User Service..."
docker build -t socialboom/user-service:latest services/user-services

echo "Building Booking Service..."
docker build -t socialboom/booking-service:latest services/booking-service

echo "Building Notification Service..."
docker build -t socialboom/notification-service:latest services/notification-service

echo "Applying Kubernetes manifests..."
kubectl apply -f k8s/namespace.yaml
kubectl apply -f k8s/secrets.yaml
kubectl apply -f k8s/network-policies.yaml
kubectl apply -f k8s/postgres/pvc.yaml
kubectl apply -f k8s/postgres/configmap.yaml
kubectl apply -f k8s/postgres/all.yaml
kubectl apply -f k8s/rabbitmq/all.yaml
kubectl apply -f k8s/notification-service/all.yaml
kubectl apply -f k8s/user-service/deployment.yaml
kubectl apply -f k8s/user-service/service.yaml
kubectl apply -f k8s/user-service/hpa.yaml
kubectl apply -f k8s/booking-service/all.yaml

echo "Installing KEDA for Scale-to-Zero capability..."
helm repo add kedacore https://kedacore.github.io/charts
helm repo update
helm upgrade --install keda kedacore/keda --namespace keda --create-namespace

echo "Applying Istio routing and KEDA rules..."
kubectl apply -f k8s/istio/all.yaml
kubectl apply -f k8s/istio/peer-authentication.yaml
kubectl apply -f k8s/istio/rate-limits.yaml
kubectl apply -f k8s/notification-service/scaledobject.yaml

echo "Deployment complete! Run 'kubectl get pods -n socialboom -w' to watch the pods spin up."
