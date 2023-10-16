# Dockerfile

FROM python:3.11-alpine3.17

WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

RUN apk update
RUN apk add postgresql-dev gcc python3-dev musl-dev libpq
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .

