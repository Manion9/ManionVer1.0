# Build stage
FROM python:3.11-slim as builder

# Configure apt and install build dependencies
RUN rm -f /etc/apt/apt.conf.d/docker-clean \
    && echo "deb https://deb.debian.org/debian/ stable main" > /etc/apt/sources.list \
    && echo 'Binary::apt::APT::Keep-Downloaded-Packages "true";' > /etc/apt/apt.conf.d/keep-cache \
    && apt-get update \
    && apt-get install -y --no-install-recommends \
    gcc \
    g++ \
    pkg-config \
    ffmpeg \
    libcairo2-dev \
    libpango1.0-dev \
    python3-dev \
    texlive \
    texlive-latex-extra \
    make \
    libpangocairo-1.0-0 \
    dvisvgm \
    && rm -rf /var/lib/apt/lists/*

# Install Poetry
RUN pip install --no-cache-dir poetry==1.7.1

WORKDIR /app
COPY pyproject.toml poetry.lock ./

# Install dependencies without project installation
RUN poetry config virtualenvs.create false \
    && poetry install --no-root

# Runtime stage
FROM python:3.11-slim

# Install runtime dependencies
RUN apt-get update \
    && echo "deb https://deb.debian.org/debian/ stable main" > /etc/apt/sources.list \
    && apt-get install -y --no-install-recommends \
    ffmpeg \
    libcairo2 \
    libpango1.0-0 \
    libpangocairo-1.0-0 \
    texlive \
    texlive-latex-extra \
    dvisvgm \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY .env .env

# Copy built packages and application
COPY --from=builder /usr/local/lib/python3.11/site-packages /usr/local/lib/python3.11/site-packages
COPY --from=builder /usr/local/bin/poetry /usr/local/bin/poetry
COPY manimator ./manimator

ENV PYTHONPATH=/app/manimator
ENV $(cat .env | xargs)
EXPOSE 7860
ENV GRADIO_SERVER_NAME="0.0.0.0"
CMD ["python", "manimator/gradio_app.py"]

# For using through APIs
# EXPOSE 8000
# CMD ["python", "-m", "uvicorn", "manimator.main:app", "--host", "0.0.0.0", "--port", "8000"]