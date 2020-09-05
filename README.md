# Github pull requests monitor

A WIP **non-production ready** minimal script to monitor github pull requests, when a user is added
as reviewer of one or more PR on one of more repositories, an icon on the system tray changes its
color.

## Configuration

### Auth

Create an oauth [token](https://github.com/settings/tokens) with the following permissions:

- `repo` (Full control of private repositories )

## Configuration file

Create a file named `gprmon.yml` at the same level of `gprmon.py`, example:

```yaml
---

# Optional (examples are default values)
interval: 30           # Interval between checks
log_level: INFO        # Log level verbosity

# Mandatory
token: "<oauth token>" # Mandatory but can be set as environment variable GITHUB_TOKEN
organization: "<your org>"
url: "https://<github url>"
user: "<user>"
repos:
  - "repo1"
  - "repo2"
  - "repon"
```
