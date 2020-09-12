# Github pull requests monitor

A WIP **non-production ready** minimal script to monitor Github pull requests. When a user is added
as a reviewer of one or more PR on one or more repositories, an icon on the system tray changes its
color.

## Configuration

### Authentication

Create an Oauth [token](https://github.com/settings/tokens) with the following permissions:

- `repo` (Full control of private repositories )

## Configuration file

Create a file named `gprmon.yml` at the same level of `gprmon.py`, example:

```yaml
---

# Optional (examples are default values)
interval: 30           # Interval between checks
log_level: INFO        # Log level verbosity
url: "https://<github url>" # for github hosted only

# Mandatory
organization: "<organization/owner of the repository>"
token: "<oauth token>" # can be set as environment variable GITHUB_TOKEN
user: "<user>"         # user to look up among the reviewers
repos:
  - "repo1"
  - "repo2"
  - "repon"
```
