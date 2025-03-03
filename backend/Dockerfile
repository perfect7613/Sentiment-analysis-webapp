# backend/Dockerfile
FROM python:3.13.2-alpine3.20

WORKDIR /app

# Install build dependencies
RUN apk add --no-cache --virtual .build-deps \
    gcc \
    musl-dev \
    python3-dev \
    libffi-dev \
    openssl-dev \
    git

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Clean up build dependencies
RUN apk del .build-deps

# Copy application code
COPY . .

# Download and cache the model during build
RUN python -c "import os; \
    from dotenv import load_dotenv; \
    load_dotenv(); \
    from transformers import AutoModelForSequenceClassification, AutoTokenizer; \
    model_name = 'tabularisai/multilingual-sentiment-analysis'; \
    hf_token = os.environ.get('HF_AUTH_TOKEN', None); \
    AutoModelForSequenceClassification.from_pretrained(model_name, use_auth_token=hf_token); \
    AutoTokenizer.from_pretrained(model_name, use_auth_token=hf_token)"

# Expose the API port
EXPOSE 8000

# Run the application
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]# backend/Dockerfile
FROM python:3.9-alpine

WORKDIR /app

# Install build dependencies
RUN apk add --no-cache --virtual .build-deps \
    gcc \
    musl-dev \
    python3-dev \
    libffi-dev \
    openssl-dev \
    git

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Clean up build dependencies
RUN apk del .build-deps

# Copy application code
COPY . .

# Download and cache the model during build
RUN python -c "import os; \
    from dotenv import load_dotenv; \
    load_dotenv(); \
    from transformers import AutoModelForSequenceClassification, AutoTokenizer; \
    model_name = 'tabularisai/multilingual-sentiment-analysis'; \
    hf_token = os.environ.get('HF_AUTH_TOKEN', None); \
    AutoModelForSequenceClassification.from_pretrained(model_name, use_auth_token=hf_token); \
    AutoTokenizer.from_pretrained(model_name, use_auth_token=hf_token)"

# Expose the API port
EXPOSE 8000

# Run the application
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]