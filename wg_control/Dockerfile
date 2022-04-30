# syntax=docker/dockerfile:1
FROM python:3.8-slim

ENV PYTHONUNBUFFERED 1
ENV DOCKER_CONTAINER 1

WORKDIR /code

COPY requirements.txt /code/
RUN apt-get update \
    && apt-get -y install libpq-dev gcc \
    && pip install -U pip \
    && pip install -r requirements.txt

COPY . /code/

