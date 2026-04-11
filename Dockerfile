# Bygg og kjør — ikke legg inn .env; bruk miljøvariabler/secrets i kjøremiljøet.
FROM python:3.12-slim
WORKDIR /app
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1

COPY pyproject.toml README.md ./
COPY src ./src
RUN pip install --no-cache-dir .

USER nobody
ENTRYPOINT ["mal-demo"]
CMD []
