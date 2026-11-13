FROM python:3.13-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    EXPENSES_DB=/data/expenses.db

WORKDIR /app

# Create a non-root user and setup /data ownership before VOLUME
RUN useradd -u 1000 appuser && \
    mkdir -p /data && \
    chown -R appuser:appuser /data /app

# Copy and install runtime dependencies first
COPY requirements-runtime.txt .
RUN pip install --no-cache-dir -r requirements-runtime.txt

# Copy application source code
COPY main.py database.py crud.py schemas.py ./

# Define volume for database storage
VOLUME ["/data"]

USER root

EXPOSE 8000

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
