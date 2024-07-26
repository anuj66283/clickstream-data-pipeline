# syntax=docker/dockerfile:1
FROM python:3.10-alpine
WORKDIR /code
RUN apk update && \
    apk add build-base gcc libressl-dev musl-dev zlib-dev ca-certificates
COPY requirements.txt .
RUN pip install --upgrade pip && \
    pip install -r requirements.txt
COPY script .
RUN chmod +x check.sh
CMD ["./check.sh"]