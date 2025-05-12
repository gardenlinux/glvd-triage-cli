FROM docker.io/library/debian:trixie

ENV PGHOST glvd
ENV PGPORT 5432
ENV PGDATABASE glvd
ENV PGUSER glvd
ENV PGPASSWORD glvd

RUN apt-get update && apt-get install -y postgresql-client

COPY tests/integration/asserts-entrypoint.sh /entrypoint.sh

ENTRYPOINT ["/entrypoint.sh"]
