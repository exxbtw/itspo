FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY proto/ proto/
RUN python -m grpc_tools.protoc \
    -I proto \
    --python_out=. \
    --grpc_python_out=. \
    proto/notifications.proto

COPY main.py grpc_server.py ./

EXPOSE 8131 50051

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8131"]
