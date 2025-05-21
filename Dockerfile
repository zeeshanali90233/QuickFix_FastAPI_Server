
ARG PYTHON_VERSION=3.12.3
FROM python:${PYTHON_VERSION}-alpine as base

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ARG UID=10001

WORKDIR /app

# Create a non-privileged user that the app will run under.
RUN adduser \
    --disabled-password \
    --gecos "" \
    --home "/nonexistent" \
    --shell "/sbin/nologin" \
    --no-create-home \
    --uid "${UID}" \
    appuser

copy requirements.txt requirements.txt
RUN python -m pip install -r requirements.txt

# Switch to the non-privileged user to run the application.
USER appuser

# Copy the source code into the container.
COPY . .

# Expose the port that the application listens on.
EXPOSE 8000

# Run the application.
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]

