# glvd-triage-cli

A command-line utility to enrich [GLVD](https://github.com/gardenlinux/glvd) with CVE context information ("triage data").

The CVE context data is maintained in [glvd-triage-data](https://github.com/gardenlinux/glvd-triage-data) as YAML files.

## Use via GitHub Actions Workflow

Trigger the workflow here https://github.com/gardenlinux/glvd-triage-data/actions/workflows/triage.yaml

## Local Usage

### Installation

Download the [glvd-triage.sh script](https://raw.githubusercontent.com/gardenlinux/glvd-triage-cli/refs/heads/main/aux/glvd-triage.sh) and make it executable:

```bash
mkdir -p ~/bin
wget --output-document ~/bin/glvd-triage https://raw.githubusercontent.com/gardenlinux/glvd-triage-cli/refs/heads/main/aux/glvd-triage.sh
chmod +x ~/bin/glvd-triage
```

Ensure `~/bin` is in your `PATH` to run `glvd-triage` from anywhere.

### Usage

Run the script to add or update CVE context information in GLVD. Refer to the script's help output for available commands and options:

```bash
glvd-triage --help
```

## Testing

This repository includes tests using a [Compose file](https://compose-spec.io) for quick iteration and validation.

To run the tests:

1. Ensure you have [Podman Compose](https://github.com/containers/podman-compose) or Docker Compose installed.
2. Configure Podman Compose to use the `docker-compose` binary if needed.
3. Create a `.gitignored` file named `github-pat.txt` in the repository root and add your GitHub Personal Access Token (PAT) to it.  
    - The PAT should be *fine-grained* with **read access** to the `gardenlinux` organization and the `gardenlinux/glvd-triage-data` repository.

Then, run the tests as described in the Compose file.
