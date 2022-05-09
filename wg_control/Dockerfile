# syntax=docker/dockerfile:1
FROM python:3.8-slim

ENV PYTHONUNBUFFERED 1
ENV DOCKER_CONTAINER 1

WORKDIR /code

COPY requirements.txt /code/
RUN apt-get update \
    && apt-get -y install libpq-dev gcc \
    && apt-get install tk -y \
    && pip install -U pip \
    && pip install -r requirements.txt \
    && apt install wireguard -y

RUN sh -c "$(wget -O- https://github.com/deluan/zsh-in-docker/releases/download/v1.1.2/zsh-in-docker.sh)" -- \
    -p git -p ssh-agent -p 'history-substring-search' \
    -a 'bindkey "\$terminfo[kcuu1]" history-substring-search-up' \
    -a 'bindkey "\$terminfo[kcud1]" history-substring-search-down'
    
COPY . /code/