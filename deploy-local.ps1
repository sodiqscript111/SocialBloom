Write-Host "Building User Service..."
docker build -t socialboom/user-service:latest services/user-services
Write-Host "Building Booking Service..."
docker build -t socialboom/booking-service:latest services/booking-service
Write-Host "Building Notification Service..."
docker build -t socialboom/notification-service:latest services/notification-service

Write-Host "Applying Kubernetes manifests..."
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

kubectl apply -f k8s/istio/all.yaml
kubectl apply -f k8s/istio/peer-authentication.yaml
kubectl apply -f k8s/istio/rate-limits.yaml

Write-Host "Deployment complete! Run 'kubectl get pods -n socialboom -w' to watch the pods spin up."
