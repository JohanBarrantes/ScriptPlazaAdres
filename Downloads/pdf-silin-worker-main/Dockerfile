FROM ubuntu:20.04

RUN apt-get clean
RUN apt-get update
RUN apt-get install -y -q ghostscript --fix-missing

ENV PYTHONPATH=/app/

RUN DEBIAN_FRONTEND="noninteractive" apt-get -y install tzdata

# Python dependencies
RUN apt-get install -y python3 python3-pip build-essential libssl-dev libffi-dev python-dev \
    # psycopg2 dependencies
    && apt-get install -y libevent-dev libc-dev \
    # CFFI dependencies
    && apt-get install -y libffi-dev \
    # Translations dependencies
    && apt-get install -y gettext
    # https://docs.djangoproject.com/en/dev/ref/django-admin/#dbshell

RUN apt-get install -y -q libreoffice
RUN apt-get install -y -q fonts-roboto

# Install and setup Supervisor
RUN apt-get install -y -q supervisor
RUN groupadd -r supervisor && usermod -a -G supervisor root
RUN mkdir -p /var/log/supervisor
ADD ./init/supervisor /etc/supervisor/conf.d

# Requirements are installed here to ensure they will be cached.
COPY ./requirements /requirements
RUN pip3 install --no-cache-dir -r /requirements/production.txt \
    && rm -rf /requirements

COPY ./init/production/django/entrypoint /entrypoint
RUN sed -i 's/\r//' /entrypoint
RUN chmod +x /entrypoint

COPY ./init/production/django/start /start
RUN sed -i 's/\r//' /start
RUN chmod +x /start

COPY . /app

WORKDIR /app

ENTRYPOINT ["/entrypoint"]

CMD [ "/start" ]