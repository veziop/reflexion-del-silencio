FROM python:3.11-slim-bookworm

WORKDIR /code

COPY ./requirements.txt /code/requirements.txt

RUN  pip install --no-cache-dir --upgrade -r /code/requirements.txt

COPY . /code/api

ENV TIMEZONE="Europe/Madrid"

RUN mkdir -p /code/data

EXPOSE 8080

CMD ["waitress-serve", "--host", "0.0.0.0", "--port", "8080", "api.main:app"]
