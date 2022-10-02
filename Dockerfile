# syntax=docker/dockerfile:1
FROM python:3
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /wis
COPY web /wis/
COPY Pipfile /wis/

RUN pip install pipenv
RUN pipenv install

