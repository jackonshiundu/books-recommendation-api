FROM python:3.9-alpine3.13
LABEL maintainer="echesajackon.com"

ENV PYTHONUNBUFFERED 1

COPY ./requirements.txt /tmp/requirements.txt
COPY ./requirements.dev.txt /tmp/requirements.dev.txt
COPY  ./app /app

WORKDIR /app

EXPOSE 8000

ARG DEV=false
RUN apk add --update --no-cache postgresql-client && \
    apk add --update --no-cache --virtual .tmp-build-deps \
        build-base \
        postgresql-dev \
        musl-dev \
        jpeg-dev \
        zlib-dev \
        libffi-dev && \
    pip install -r /tmp/requirements.txt && \
    if [ "$DEV"='true' ]; \
        then pip install -r /tmp/requirements.dev.txt; fi && \
    apk del .tmp-build-deps && \
    mkdir -p /app/media/covers && \ 
    mkdir -p /app/staticfiles && \   
    adduser --disabled-password --no-create-home django-user &&\
    chown -R django-user:django-user /app/media &&\
    chown -R django-user:django-user /app/staticfiles


USER django-user

CMD ["sh", "-c", "python manage.py migrate && python manage.py collectstatic --no-input && gunicorn --bind 0.0.0.0:8000 app.wsgi:application"]
