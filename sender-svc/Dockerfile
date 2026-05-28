FROM python:3.11-slim

WORKDIR /app

COPY sender-svc/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY notifications-svc/proto/ proto/
RUN python -m grpc_tools.protoc \
    -I proto \
    --python_out=. \
    --grpc_python_out=. \
    proto/notifications.proto

COPY sender-svc/main.py .

EXPOSE 50052

CMD ["python", "main.py"]