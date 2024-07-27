# syntax=docker/dockerfile:1
FROM bitnami/spark:3.4.3
WORKDIR /opt/bitnami/spark
COPY requirements.txt .
RUN pip install --upgrade pip && \
    pip install -r requirements.txt