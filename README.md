# MOR Core
Description

## Tech Stack
[Turbo JS](https://turbo.hotwired.dev/), [SCSS](https://sass-lang.com/)

## Get Started 🚀
To get started, install [Docker](https://www.docker.com/)

### Create local dns entry
Add '127.0.0.1  core.mor.local' to your hosts file

### create docker networks
~~~bash
    docker network create core_network
    docker network create mor_bridge_network
~~~

### Build and run Docker container
~~~bash
    docker compose build

    docker compose up
~~~

Authorize via the Django admin: http://core.mor.local:8002/admin/
You can view the website on http://core.mor.local:8002.

# Current db schema (24-09-2023)
![db_schema](db_schema.svg)
