# glvd-triage-cli

Utility to add CVE context information to GLVD.

Data is maintained [here](https://github.com/gardenlinux/glvd-triage-data) in yaml files.

Example usage:

```
kubectl run glvd-triage-$(date +%s) --image=ghcr.io/gardenlinux/triage:latest --restart=Never --env=PGHOST=glvd-database-0.glvd-database --env=PGPASSWORD=$(kubectl get secret/postgres-credentials --template="{{.data.password}}" | base64 -d) --env=GLVD_TRIAGE_FILE=sample.yaml --env=PAT=YOUR_PAT
```
