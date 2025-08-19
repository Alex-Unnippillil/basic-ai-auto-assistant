FROM python:3.11-slim

WORKDIR /app
COPY . /app

RUN pip install --no-cache-dir -e .[full] fastapi uvicorn[standard]

CMD ["uvicorn", "server.main:app", "--host", "0.0.0.0", "--port", "8000"]
