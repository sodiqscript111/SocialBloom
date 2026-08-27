# SocialBoom System Architecture & Network Flow

This document outlines the end-to-end architecture, Kubernetes scaling strategies, and the deep-dive network flow of Istio within the SocialBoom microservice ecosystem.

---

## 1. End-to-End System Overview

SocialBoom is a microservice-based platform built for influencer and brand interactions. It is designed to be highly available, scalable, and secure.

### The Microservices (The Workloads)
1. **User Service (REST / HTTP):** Handles user registration, JWT authentication, and profiles.
2. **Booking Service (REST / HTTP):** Manages campaigns, payments, and influencer bookings.
3. **Notification Service (gRPC / Async):** A high-speed service written in Go that handles sending emails and alerts.

### The Backing Services (State & Queues)
4. **PostgreSQL:** The relational database storing persistent state (users, bookings, campaigns).
5. **RabbitMQ:** The asynchronous message broker used for decoupling heavy tasks (e.g., emitting a `booking_created` event so the Notification Service can process it without blocking the user).

---

## 2. Kubernetes Pods & Scaling

### Current Pod Count
In our local deployment, we are running **5 application pods** and **2 system pods**:
- `user-service` (1 Pod)
- `booking-service` (1 Pod)
- `notification-service` (1 Pod)
- `postgres` (1 Pod)
- `rabbitmq` (1 Pod)
- *Istio System:* `istio-ingressgateway` (1 Pod) & `istiod` (1 Pod)

### How We Scale (The Basics)
Currently, scaling is managed by the Kubernetes **Horizontal Pod Autoscaler (HPA)**. The HPA continuously monitors the CPU and Memory metrics of the pods. If the `user-service` CPU utilization exceeds 70%, the HPA dynamically provisions additional replicas (up to a maximum limit). 

---

## 3. Advanced Network Auto-Scaling (Istio + KEDA)

Scaling on CPU is standard, but it isn't always smart. As you noted, we can use Istio's network metrics to scale more intelligently. However, we must be careful with our **scaling conditions** to prevent cascading system failures.

### ❌ The Danger: Scaling on Latency
If the PostgreSQL database becomes overwhelmed, database queries will slow down. This causes the `booking-service` HTTP latency to spike. 
If we configured our autoscaler to say: *"Scale up when latency > 500ms,"* Kubernetes would spin up 10 new `booking-service` pods. Those 10 new pods would instantly open new connections to the already-dying database, **crashing the database completely.** 

### ✅ The Solution: Smart Scaling Conditions
To scale safely without destroying downstream systems, we use **KEDA (Kubernetes Event-driven Autoscaling)** hooked into Istio and RabbitMQ:

1. **Condition 1: Scale on Queue Depth (For Async Workers)**
   - *Logic:* "If the `booking_events` queue in RabbitMQ exceeds 50 pending messages, scale up the `notification-service`."
   - *Why it's safe:* The notification service consumes messages; it doesn't query the main database. Scaling it up simply drains the queue faster without harming the rest of the system.
2. **Condition 2: Scale on Request Volume / RPS (For APIs)**
   - *Logic:* "If the Istio Ingress Gateway reports that the `user-service` is receiving > 200 Requests Per Second (RPS), scale up the `user-service`."
   - *Why it's safe:* We are scaling based on actual user demand (volume), not downstream slowness (latency).
3. **Condition 3: Circuit Breaking (For Downstream Protection)**
   - *Logic:* We don't scale when a service fails; we cut it off. We use Istio `DestinationRules` so that if a pod returns five `5xx` server errors in a row, Istio "ejects" that pod from the load balancer pool for 1 minute, preventing traffic from hitting a broken instance.

---

## 4. End-to-End Istio Message Flow

Istio operates using a **Data Plane** (Envoy sidecar proxies) and a **Control Plane** (`istiod`). Here is the exact lifecycle of a single request from a client's browser, through the mesh, and back.

### Step 1: The Client Request (Ingress)
1. A user clicks "Login" on their browser. An HTTP POST request is sent to `http://socialboom.com/login`.
2. The request hits the **Istio Ingress Gateway** (which acts as our L7 Load Balancer).
3. The Gateway **terminates** the client's external HTTP/TCP connection. 
4. The Gateway reads the URL path (`/login`), checks the `VirtualService` rules, and determines the request belongs to the `user-service`.

### Step 2: Entering the Mesh (mTLS & Sidecars)
5. The Gateway initiates a brand new, strictly encrypted **mTLS (Mutual TLS)** tunnel to one of the `user-service` pods. 
6. The traffic arrives at the `user-service` pod, but it does *not* hit your Python code yet. It is intercepted by the **Envoy Proxy Sidecar**.
7. The Envoy Sidecar verifies the mTLS certificate. It then checks our `EnvoyFilter` rules (e.g., checking the token bucket to ensure the client hasn't exceeded 100 requests per second).
8. Once validated, the Envoy sidecar forwards the traffic locally (via `localhost`) to your FastAPI Python application.

### Step 3: Service-to-Service Communication
9. Let's assume the `user-service` now needs to call the `notification-service` via gRPC. 
10. Your Python code simply sends a raw HTTP/2 gRPC request to `notification-service:50051`.
11. The outbound request is instantly intercepted by the `user-service`'s Envoy sidecar.
12. The sidecar wraps the raw request in mTLS encryption and securely transmits it to the `notification-service`'s Envoy sidecar, which decrypts it and passes it to the Go application.

### Step 4: The Response (Egress)
13. The Go app processes the data and sends a response back through its local sidecar.
14. The Python `user-service` finishes processing and returns a JSON response (e.g., the JWT Token) to *its* local sidecar.
15. The sidecar transmits the encrypted JSON back to the Istio Ingress Gateway.
16. The Gateway decrypts the internal mTLS payload, wraps it back into a standard external HTTP response, and sends it to the user's browser, finally **terminating** the transaction.

---

## 5. Technical Specifications Used

- **External APIs:** REST (HTTP/1.1) built on Python FastAPI.
- **Internal APIs:** gRPC (HTTP/2 with Protocol Buffers) for highly efficient, strongly-typed synchronous communication between microservices.
- **Asynchronous Events:** AMQP 0-9-1 (RabbitMQ) for decoupled, non-blocking event streaming (e.g., `user_registered`, `booking_created`).
- **Service Mesh:** Istio 1.22 (Envoy Proxies) enforcing Strict mTLS, L7 Routing, and Local Rate Limiting.
- **Network Security:** Kubernetes Layer 4 `NetworkPolicies` enforcing a Default-Deny, Zero-Trust posture inside the cluster namespace.
- **Database:** PostgreSQL accessed via SQLAlchemy ORM.
