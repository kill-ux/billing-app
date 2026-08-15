FROM alpine:3.18

WORKDIR /app

RUN apk add --no-cache python3 py3-pip && \
    adduser -D appuser

COPY ./requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

COPY ./app ./app
COPY ./server.py ./server.py

RUN chown -R appuser:appuser /app
USER appuser

HEALTHCHECK --interval=5s \
            --timeout=5s \
            --start-period=30s \
            --retries=10 \
    CMD wget --no-verbose --tries=1 --spider \
        http://127.0.0.1:8000/health || exit 1

ENTRYPOINT ["python3", "server.py"]
