# SocialBoom: My Service Mesh Learning Playground

Welcome to **SocialBoom**! While on the surface this looks like a microservice platform connecting brands and influencers, this repository actually serves as my advanced engineering playground for exploring **Cloud-Native Architecture, Kubernetes, Istio, and Envoy proxy mechanics.**

I built this project specifically to get hands-on experience with Service Mesh concepts, zero-trust security, and event-driven auto-scaling.

## The Architecture Playground

This project is orchestrated using **Kubernetes** and networked using the **Istio Service Mesh**. Rather than relying on simple API gateways, I implemented advanced L7 proxy features by manipulating Envoy sidecars directly.

### The Tech Stack
*   **Compute:** Kubernetes, Docker
*   **Service Mesh:** Istio 1.22, Envoy Proxies
*   **Auto-scaling:** KEDA (Kubernetes Event-driven Autoscaling)
*   **Microservices:** Python (FastAPI), Go (gRPC)
*   **State & Messaging:** PostgreSQL, RabbitMQ (AMQP)

---

## Service Mesh Features Explored

I used this project to learn and implement the following advanced Istio/Envoy features:

### 1. Zero-Trust Security (Strict mTLS)
By deploying a `PeerAuthentication` policy, the entire `socialboom` namespace operates in **STRICT mTLS mode**. Every single byte of traffic between the microservices is automatically encrypted by the Envoy sidecars, requiring zero cryptographic code in the Python or Go applications.

### 2. The Envoy Escape Hatch (Token-Bucket Rate Limiting)
Instead of relying on a global Redis cluster for rate limiting, I bypassed standard Istio controls and used an `EnvoyFilter` to inject a **Token-Bucket Rate Limiter** directly into the Envoy sidecars. 
*   This caps traffic at 100 requests per second *per pod*.
*   If a pod gets flooded, the Envoy proxy instantly rejects the traffic (HTTP 429) before it ever wakes up the Python application.

### 3. Circuit Breaking
I configured Istio `DestinationRules` to monitor the health of upstream pods. If a pod returns five consecutive `5xx` server errors, Istio automatically "ejects" that specific pod from the load balancer pool for 1 minute to prevent cascading system failures.

### 4. Multi-Protocol Sniffing
The mesh natively handles both HTTP/1.1 (REST) for the User and Booking services, and HTTP/2 (gRPC) for the Notification service. By specifying port protocols in the Kubernetes services (`name: grpc`), Istio instantly optimizes the Envoy proxies without needing to sniff the connection bytes.

---

## Event-Driven Auto-Scaling (Scale-to-Zero)

To explore advanced scaling beyond standard CPU metrics, I implemented **KEDA**.

Instead of scaling the `notification-service` based on CPU usage, KEDA directly queries the RabbitMQ `user_booking_events_queue`. 
*   **Scale to Zero:** If the queue is empty, KEDA kills all notification pods to save cluster resources (0 replicas).
*   **Event-Driven:** For every 10 messages that drop into the queue, KEDA instantly spins up a new pod to drain the queue rapidly.
