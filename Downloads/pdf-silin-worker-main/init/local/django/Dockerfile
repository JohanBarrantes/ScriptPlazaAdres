FROM ubuntu:20.04

RUN apt-get clean
RUN apt-get update
RUN apt-get install -y -q ghostscript --fix-missing

RUN DEBIAN_FRONTEND="noninteractive" apt-get -y install tzdata

# Python dependencies
RUN apt-get install -y python3 python3-pip build-essential libssl-dev libffi-dev python-dev --fix-missing \
    # psycopg2 dependencies
    && apt-get install -y libevent-dev libc-dev --fix-missing \
    # CFFI dependencies
    && apt-get install -y libffi-dev --fix-missing \
    # Translations dependencies
    && apt-get install -y gettext --fix-missing
    # https://docs.djangoproject.com/en/dev/ref/django-admin/#dbshell

RUN apt-get install -y -q libreoffice --fix-missing
RUN apt-get install -y -q fonts-roboto

# Install and setup Supervisor
RUN apt-get install -y -q supervisor
RUN groupadd -r supervisor && usermod -a -G supervisor root
RUN mkdir -p /var/log/supervisor
ADD ./init/supervisor /etc/supervisor/conf.d

# Requirements are installed here to ensure they will be cached.
COPY ./requirements /requirements
RUN pip install -r /requirements/local.txt

COPY ./init/production/django/entrypoint /entrypoint
RUN sed -i 's/\r//' /entrypoint
RUN chmod +x /entrypoint

COPY ./init/local/django/start /start
RUN sed -i 's/\r//' /start
RUN chmod +x /start

WORKDIR /app

RUN apt-get install -y -q htop nmap