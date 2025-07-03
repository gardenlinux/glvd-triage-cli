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
    echo "Usage: $SCRIPT_NAME [-t <image-tag>] path/to/triage/files my-github-pat"
    echo "  -t <image-tag>   Optional. Use a specific tag for the triage image (default: latest)"
    echo ""
    exit 1
}

main() {
    local image_tag="latest"

    # Parse flags
    while [[ $# -gt 0 ]]; do
        case "$1" in
            -t|--tag)
                shift
                [[ $# -gt 0 ]] || usage
                image_tag="$1"
                shift
                ;;
            -*)
                usage
                ;;
            *)
                break
                ;;
        esac
    done

    [[ $# -ge 2 ]] || usage
    [[ -n "$1" ]] || usage
    [[ -n "$2" ]] || usage
    local triage_dir="${1}"; shift
    local github_pat="${1}"; shift

    echo "Test if glvd-database-0 exists"
    echo "We need this, be sure you have the correct kubeconfig set"
    kubectl get pods glvd-database-0 || usage

    local now
    now="$(date +%s)"

    kubectl run glvd-triage-"$now" \
     --image=ghcr.io/gardenlinux/triage:"$image_tag" \
     --restart=Never \
     --env=PGHOST=glvd-database-0.glvd-database \
     --env=PGPASSWORD="$(kubectl get secret/postgres-credentials --template="{{.data.password}}" | base64 -d)" \
     --env=GLVD_TRIAGE_DIR="$triage_dir" \
     --env=PAT="$github_pat"
}

main "$@"
