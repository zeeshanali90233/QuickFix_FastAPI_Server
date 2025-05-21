ARG PYTHON_VERSION=3.12.3
FROM python:3.12-slim as base

# Environment settings
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Create working directory
WORKDIR /app

# Install required build dependencies
RUN apk add --no-cache \
    bash \
    build-base \
    libffi-dev \
    openssl-dev \
    python3-dev \
    musl-dev \
    freetype-dev \
    libpng-dev \
    openblas-dev \
    jpeg-dev \
    zlib-dev \
    cargo \
    git \
    curl

# Create a non-root user
ARG UID=10001
RUN adduser \
    --disabled-password \
    --gecos "" \
    --home "/nonexistent" \
    --shell "/sbin/nologin" \
    --no-create-home \
    --uid "${UID}" \
    appuser

# Copy requirements first and install them
COPY requirements.txt .

# Upgrade pip and install Python packages
RUN pip install --upgrade pip \
    && pip install --no-cache-dir -r requirements.txt

# Switch to non-root user
USER appuser

# Copy the rest of the project
COPY . .

# Expose app port
EXPOSE 8000

# Start the application
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
