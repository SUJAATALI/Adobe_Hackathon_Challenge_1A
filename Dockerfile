FROM --platform=linux/amd64 python:3.10

WORKDIR /app

# Install system dependencies for PyMuPDF and spaCy
RUN apt-get update && apt-get install -y gcc

# Copy your code
COPY src/ ./src/

# Install Python dependencies
RUN pip install --upgrade pip \
    && pip install pymupdf langdetect spacy

# Download spaCy models
RUN python -m spacy download en_core_web_sm
RUN python -m spacy download es_core_news_sm
RUN python -m spacy download ja_core_news_sm

# Set entrypoint
CMD ["python", "src/process_pdfs.py"]