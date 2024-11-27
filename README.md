# glvd-triage-cli



```
kubectl run my-triage --image=ghcr.io/gardenlinux/triage:latest --restart=Never --env=PGHOST=glvd-database-0.glvd-database --env=PGPASSWORD=$(kubectl get secret/postgres-credentials --template="{{.data.password}}" | base64 -d) --env=GLVD_TRIAGE_FILE=sample.yaml
```
