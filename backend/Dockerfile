FROM python:3.11-slim

WORKDIR /app

ARG HF_AUTH_TOKEN

# Set as environment variable for the build process
ENV HF_AUTH_TOKEN=${HF_AUTH_TOKEN}

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    git \
    && rm -rf /var/lib/apt/lists/*

COPY backend/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY backend .

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
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]