# ====================
# Stage 1: Build Image
# ====================
FROM python:3.12-slim as builder

WORKDIR /app

# Set environment variables for faster pip installs
ENV DEBIAN_FRONTEND=noninteractive \
    TRANSFORMERS_CACHE=/app/hf_models \
    HF_HOME=/app/hf_models

# Install OS dependencies
RUN apt-get update && apt-get install -y \
    git build-essential curl \
    && apt-get clean && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt .
RUN pip install --upgrade pip && pip install --no-cache-dir -r requirements.txt

# Pre-download Hugging Face models
RUN python -c "from transformers import pipeline; pipeline('sentiment-analysis', model='cardiffnlp/twitter-roberta-base-sentiment')"
RUN python -c "from transformers import pipeline; pipeline('zero-shot-classification', model='facebook/bart-large-mnli')"
RUN python -c "from transformers import pipeline; pipeline('ner', model='dslim/bert-base-NER')"
RUN python -c "from sentence_transformers import SentenceTransformer; SentenceTransformer('all-MiniLM-L6-v2')"

# ======================
# Stage 2: Runtime Image
# ======================
FROM python:3.12-slim

WORKDIR /app

# Copy dependencies and models from builder
COPY --from=builder /usr/local/lib/python3.12/site-packages /usr/local/lib/python3.12/site-packages
COPY --from=builder /usr/local/bin /usr/local/bin
COPY --from=builder /app/hf_models /app/hf_models

# Environment for offline use
ENV TRANSFORMERS_CACHE=/app/hf_models \
    HF_HOME=/app/hf_models \
    PREPROCESS_CONFIG=config/preprocess_config.yaml \
    LABELING_CONFIG=config/labeling_config.yaml

# Copy application code
COPY . .

# Entry point script — Choose based on ENV or override in CMD
CMD ["python", "scripts/run_data_pipeline.py"]
# For labeling: override with scripts/run_labeling_pipeline.py

