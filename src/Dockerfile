# syntax=docker/dockerfile:1
FROM python:3.10-alpine

WORKDIR /code

COPY requirements.txt .

RUN apk add git && \
    pip install --upgrade pip && \
    pip install -r requirements.txt && \
    pip install git+https://github.com/anuj66283/faker-clickstream
    
CMD ["uvicorn", "generator:app", "--host", "0.0.0.0", "--port", "8000"]
