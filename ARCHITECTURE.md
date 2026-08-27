# SocialBoom System Architecture

SocialBoom is a microservice-based platform designed to connect brands with influencers for marketing campaigns. The architecture is built for high availability, secure service-to-service communication, and event-driven scalability.

---

## 1. High-Level Architecture Overview

The system follows a domain-driven microservice architecture, containerized via Docker, and orchestrated by Kubernetes. The application relies on asynchronous event-driven patterns for background processing and high-speed synchronous protocols for internal communication.

### Core Microservices

1. **User Service (Python / FastAPI)**
   - **Responsibility:** Manages user authentication, JWT generation, and creator/brand profiles.
   - **API Protocol:** REST (HTTP/1.1) for external clients.
   - **Database:** Connects to the `testing` PostgreSQL schema.

2. **Booking Service (Python / FastAPI)**
   - **Responsibility:** Handles campaign creation, influencer booking workflows, and payment tracking.
   - **API Protocol:** REST (HTTP/1.1) for external clients; gRPC for internal upstream calls.
   - **Database:** Connects to the `bookingsdb` PostgreSQL schema.

3. **Notification Service (Go)**
   - **Responsibility:** A high-speed background worker responsible for dispatching email and platform alerts.
   - **API Protocol:** gRPC (HTTP/2) for synchronous triggers; AMQP for asynchronous event processing.
   - **Database:** Connects to the `notificationsdb` PostgreSQL schema.

---


## 2. Communication Patterns

SocialBoom utilizes multiple protocols to optimize performance based on the specific communication requirement:

- **External Traffic (REST):** All external client traffic (e.g., from web or mobile apps) enters the cluster via RESTful HTTP/1.1 endpoints.
- **Internal Synchronous (gRPC):** When the Booking Service needs immediate, synchronous data from the Notification Service, it bypasses HTTP/1.1 and uses gRPC (HTTP/2 with Protocol Buffers) for highly efficient, strongly-typed data transfer.
- **Internal Asynchronous (AMQP):** When a process does not require an immediate response (e.g., sending a welcome email after registration), the emitting service drops an event payload into **RabbitMQ**. The Notification Service independently consumes these messages, completely decoupling the workload and preventing API timeouts.

---

## 3. Data Storage & State Management

The platform separates compute workloads from stateful data stores to ensure high resilience.

- **Relational Database (PostgreSQL):** Used as the primary data store. Strict relational mapping (via SQLAlchemy) ensures ACID compliance for sensitive data like payments and user credentials.
- **Message Broker (RabbitMQ):** Facilitates the event-driven architecture. Queues (such as `user_booking_events_queue`) provide durability, ensuring no background tasks are lost if a worker pod crashes.

---

## 4. Infrastructure & Network Security (Istio Service Mesh)

The underlying network infrastructure is powered by the **Istio Service Mesh**, providing zero-trust security and intelligent traffic management without requiring changes to the application code.

- **Ingress Gateway:** Acts as the single L7 load balancer, terminating external connections and routing traffic to the appropriate microservice using `VirtualService` rules.
- **Mutual TLS (mTLS):** Enforced in `STRICT` mode via `PeerAuthentication`. All service-to-service traffic is automatically encrypted by Envoy sidecar proxies.
- **Rate Limiting:** `EnvoyFilter` configurations inject Local Token-Bucket rate limiters (capped at 100 req/sec) directly into the sidecars to protect APIs from DDoS attacks or spam.
- **Circuit Breaking:** `DestinationRules` monitor pod health. If a pod returns consecutive 5xx errors, it is temporarily ejected from the routing pool to prevent cascading failures.
- **Network Policies:** Kubernetes Layer 4 policies enforce a default-deny posture, ensuring that pods can only communicate on explicitly allowed ports (e.g., blocking unauthorized access to the database).

---

## 5. Autoscaling Strategy

To optimize cloud resource costs while maintaining performance during traffic spikes, SocialBoom implements a multi-tiered scaling strategy:

1. **API Auto-Scaling (HPA):**
   - The User and Booking REST APIs are scaled dynamically using the native Kubernetes Horizontal Pod Autoscaler (HPA). If CPU utilization crosses 70%, additional replicas are provisioned.

2. **Event-Driven Scale-to-Zero (KEDA):**
   - The Notification Service operates as a stateless background worker.
   - Using **Kubernetes Event-driven Autoscaling (KEDA)**, the service scales based directly on RabbitMQ queue depth rather than CPU.
   - If the queue is empty, the service scales to **0 replicas** to eliminate idle resource costs. For every 10 pending messages, a new replica is spun up to rapidly drain the queue.
