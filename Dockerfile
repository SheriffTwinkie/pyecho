FROM python:3.11-slim

WORKDIR /app

COPY echo-server.py .

RUN pip install --no-cache-dir --upgrade pip

ENTRYPOINT ["python", "echo-server.py"]
