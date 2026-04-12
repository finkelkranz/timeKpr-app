# Bygg og kjør — ikke legg inn .env; bruk miljøvariabler/secrets i kjøremiljøet.
FROM python:3.12-slim

# Install dbus system libraries
RUN apt-get update && apt-get install -y \
    libdbus-1-dev \
    pkg-config \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1

COPY pyproject.toml README.md ./
COPY src ./src
RUN pip install --no-cache-dir .

USER nobody
ENTRYPOINT ["timekpr-app"]
CMD []
