FROM python:3.10-slim

WORKDIR /app

# Install system dependencies for psycopg and other packages
RUN apt-get update && apt-get install -y libpq-dev gcc && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy source code
COPY . .

# Generate gRPC client protos
RUN python -m grpc_tools.protoc -Igrpc_clients/protos --python_out=grpc_clients/protos --grpc_python_out=grpc_clients/protos grpc_clients/protos/notification.proto

EXPOSE 8001

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8001"]
