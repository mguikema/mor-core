# FROM python:3.9.6-slim-buster
FROM python:3.10.10-slim-bullseye

ENV PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=off \
    REQUESTS_CA_BUNDLE=/etc/ssl/certs/ca-certificates.crt

WORKDIR /app
COPY requirements.txt /requirements.txt

RUN apt-get update \
 && apt-get dist-upgrade -y \
 && apt-get autoremove -y \
 && apt-get install --no-install-recommends -y \
        # unzip \
        # wget \
        # dnsutils \
        # vim-tiny \
        # net-tools \
        # netcat \
        # libgeos-3.7 \
        # gdal-bin \
        # postgresql-client-11 \
        # libgdal20 \
        # libspatialite7 \
        # libfreexl1 \
        # libgeotiff2 \
        # libwebp6 \
        # proj-bin \
        # mime-support \
        # gettext \
        # libwebpmux3 \
        # libwebpdemux2 \
        # libxml2 \
        # libfreetype6 \
        # libtiff5 \

        unzip \
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

    && rm -rf /var/lib/apt/lists/* /var/cache/debconf/*-old \
    && pip install --upgrade pip \

    && pip install --no-cache-dir -r /requirements.txt \
    && apt-get purge -y gcc \
    && rm -rf /var/lib/apt/lists/* \

    && update-ca-certificates



# COPY requirements.txt /requirements.txt

# RUN apt-get update \
#     && apt-get install -y \
#         libgdk-pixbuf2.0-0 \
#         libmagic1 \
#         libcairo2 \
#         libpango1.0-0 \
#         gcc \
#         graphviz \
#         graphviz-dev \
#         git \
#     && pip install --no-cache-dir -r /requirements.txt \
#     && apt-get purge -y gcc \
#     && rm -rf /var/lib/apt/lists/*

# RUN pip install django-db-schema-renderer==0.1.1
COPY . /app/

RUN mkdir -p /media && mkdir -p /static && chown 2000 /media && chown 2000 /static

RUN mkdir -p /srv/web/var/cache && chown 2000 /srv/web/var/cache

RUN chmod +x /app/deploy/docker-entrypoint.sh && chown root:root /app/deploy/docker-entrypoint.sh

# RUN pip install --no-cache-dir -r /app/requirements.txt

CMD ["bash", "/app/deploy/docker-entrypoint.sh"]
