#!/bin/bash
set -o nounset
set -o errexit

SCRIPT_NAME="${0##*/}"
readonly SCRIPT_NAME

usage() {
    echo "Script to apply new triage data to the glvd database"
    echo ""
    echo "Requirements:"
    echo "  - This script requires access to the 'glvd' gardener cluster via kubectl"
    echo "    Be sure to set the KUBECONFIG environment variable accordingly."
    echo "  - This script requires a github personal access token with read access to https://github.com/gardenlinux/glvd-triage-data"
    echo ""
    echo "Usage: $SCRIPT_NAME my-triage-file.yaml my-github-pat"
    echo ""
    exit 1
}

main() {
    [[ $# -ge 2 ]] || usage
    [[ -n "$1" ]] || usage
    [[ -n "$2" ]] || usage
    local triage_file="${1}"; shift
    local github_pat="${1}"; shift

    echo "Test if glvd-database-0 exists"
    echo "We need this, be sure you have the correct kubeconfig set"
    kubectl get pods glvd-database-0 || usage

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

[[ $# -ge 2 ]] || usage
main "${@}"
