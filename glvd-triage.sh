#!/bin/bash
set -o nounset
set -o errexit

# Script to apply new triage data to the glvd database
# This script requires access to the `glvd` gardener cluster via kubectl

SCRIPT_NAME="${0##*/}"
readonly SCRIPT_NAME

usage() {
    echo "Usage: $SCRIPT_NAME my-triage-file.yaml my-github-pat"
    exit 1
}

main() {
    [[ $# -ge 2 ]] || usage
    [[ -n "$1" ]] || usage
    [[ -n "$2" ]] || usage
    local triage_file="${1}"; shift
    local github_pat="${1}"; shift

    local now
    now="$(date +%s)"

    kubectl run glvd-triage-"$now" \
     --image=ghcr.io/gardenlinux/triage:latest \
     --restart=Never \
     --env=PGHOST=glvd-database-0.glvd-database \
     --env=PGPASSWORD="$(kubectl get secret/postgres-credentials --template="{{.data.password}}" | base64 -d)" \
     --env=GLVD_TRIAGE_FILE="$triage_file" \
     --env=PAT="$github_pat"
}

main "${@}"

