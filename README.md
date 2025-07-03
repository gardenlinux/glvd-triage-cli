# glvd-triage-cli

Utility to add CVE context information to GLVD.

Data is maintained [here](https://github.com/gardenlinux/glvd-triage-data) in yaml files.

## usage

Download the [glvd-triage.sh script](https://raw.githubusercontent.com/gardenlinux/glvd-triage-cli/refs/heads/main/aux/glvd-triage.sh), for example like this:

```bash
mkdir -p ~/bin
wget --output-document ~/bin/glvd-triage https://raw.githubusercontent.com/gardenlinux/glvd-triage-cli/refs/heads/main/aux/glvd-triage.sh
chmod +x ~/bin/glvd-triage
```

## tests

This repo contains tets as a [compose file](https://compose-spec.io).
This setup allows to quickly iterate based on defined data.

To run the tests:

* Setup podman compose to use the `docker-compose` binary
* Create a (gitignored) `github-pat.txt` file in this directory and put your own PAT there
