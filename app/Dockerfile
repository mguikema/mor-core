FROM python:3.10.10-slim-bullseye

EXPOSE 8000

ENV APP_HOME=/app
ENV APP_USER=appuser
ENV APP_USER_ID=2000

# RUN useradd -u  --system --no-create-home 2000 docker
RUN groupadd -r $APP_USER && \
    useradd -r -u $APP_USER_ID -g $APP_USER -d $APP_HOME -s /sbin/nologin -c "Docker image user" $APP_USER

ENV PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=off \
    REQUESTS_CA_BUNDLE=/etc/ssl/certs/ca-certificates.crt

WORKDIR /app
COPY requirements.txt /requirements.txt

RUN apt-get update \
 && apt-get dist-upgrade -y \
 && apt-get autoremove -y \
 && apt-get install --no-install-recommends -y \
        build-essential \
        python-dev \
        unzip \
        curl \
        wget \
        dnsutils \
        vim-tiny \
        net-tools \
        netcat \
        libgeos-c1v5 \
        gdal-bin \
        postgresql-client \
        libgdal28 \
        libspatialite7 \
        libfreexl1 \
        libgeotiff-dev \
        libwebp6 \
        proj-bin \
        mime-support \
        gettext \
        libwebpmux3 \
        libwebpdemux2 \
        libxml2 \
        libfreetype6 \
        libtiff5 \
        libgdk-pixbuf2.0-0 \
        libmagic1 \
        libcairo2 \
        libpango1.0-0 \
        gcc \
        graphviz \
        graphviz-dev \
        git \
        locales \
    && rm -rf /var/lib/apt/lists/* /var/cache/debconf/*-old \
    && pip install --upgrade pip \
    && pip install --no-cache-dir -r /requirements.txt \
    && sed -i '/nl_NL.UTF-8/s/^# //g' /etc/locale.gen \
    && locale-gen \
    && apt-get purge -y gcc \
    && rm -rf /var/lib/apt/lists/* \
    && update-ca-certificates

ENV LANG=nl_NL.UTF-8 \
    LANGUAGE=nl_NL \
    LC_ALL=nl_NL.UTF-8

COPY . /app/

RUN mkdir -p /media && mkdir -p /static && chown $APP_USER:$APP_USER /media && chown $APP_USER:$APP_USER /static && chmod 744 /media && chmod 744 /static

RUN mkdir -p /srv/web/var/cache && chown $APP_USER:$APP_USER /srv/web/var/cache && chmod -R ugo+rwx /srv/web/var/cache

RUN chmod +x /app/deploy/docker-entrypoint.sh && chown $APP_USER:$APP_USER /app/deploy/docker-entrypoint.sh \
    && chmod +x /app/deploy/tests.sh && chown $APP_USER:$APP_USER /app/deploy/tests.sh \
    && chmod +x /app/deploy/wait-for.sh && chown $APP_USER:$APP_USER /app/deploy/wait-for.sh

RUN chown -R $APP_USER:$APP_USER $APP_HOME

USER $APP_USER
CMD ["bash", "/app/deploy/docker-entrypoint.sh"]
