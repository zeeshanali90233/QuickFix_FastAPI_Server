# Use a specific Python version with Alpine as base
ARG PYTHON_VERSION=3.12.3
FROM python:${PYTHON_VERSION}-alpine as base

# Environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ARG UID=10001

# Set the working directory
WORKDIR /app

# Install build tools and dependencies required to compile packages like scikit-learn
RUN apk update && apk add --no-cache \
    build-base \
    musl-dev \
    libffi-dev \
    gcc \
    g++ \
    make \
    python3-dev \
    py3-pip \
    py3-wheel \
    py3-setuptools \
    openblas-dev \
    lapack-dev \
    && rm -rf /var/cache/apk/*

# Create a non-privileged user
RUN adduser \
    --disabled-password \
    --gecos "" \
    --home "/nonexistent" \
    --shell "/sbin/nologin" \
    --no-create-home \
    --uid "${UID}" \
    appuser

# Copy and install Python dependencies
COPY requirements.txt .
RUN pip install --upgrade pip setuptools wheel
RUN pip install -r requirements.txt

# Switch to the non-privileged user
USER appuser

# Copy application code
COPY . .

# Expose app port
EXPOSE 8000

# Run the FastAPI app with Uvicorn
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
