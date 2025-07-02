build:
	podman build -t localhost/glvd-postgres-triage-cli-test-container:latest .

run:
	podman run -it --rm --name=glvd-postgres-sample-data --publish 5432:5432 --env POSTGRES_USER=glvd --env POSTGRES_DB=glvd --env POSTGRES_PASSWORD=glvd localhost/glvd-postgres-triage-cli-test-container:latest postgres -c log_statement=all
