FROM docker.io/library/debian:trixie

ENV PGHOST glvd
ENV PGPORT 5432
ENV PGDATABASE glvd
ENV PGUSER glvd
ENV PGPASSWORD glvd

RUN apt-get update && apt-get install -y python3-pytest python3-yaml python3-psycopg2

RUN mkdir /testdata

COPY tests/integration/assert.py /assert.py

ENTRYPOINT ["pytest", "-vvv", "/assert.py"]
