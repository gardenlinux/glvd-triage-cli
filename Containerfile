FROM debian:trixie

ENV PGHOST glvd
ENV PGPORT 5432
ENV PGDATABASE glvd
ENV PGUSER glvd
ENV PGPASSWORD glvd

RUN apt-get update && apt-get install -y postgresql-client curl python3-yaml

COPY cli.py /cli.py
COPY entrypoint.sh /entrypoint.sh

ENTRYPOINT ["/entrypoint.sh"]
