FROM python:3.10-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y libpq-dev gcc && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy source code
COPY . .

# Generate protos
RUN python -m grpc_tools.protoc -I. --python_out=. --grpc_python_out=. protos/notification.proto

EXPOSE 50051

CMD ["python", "server.py"]
