# Github pull requests monitor

A WIP **non-production ready** minimal script to monitor github pull requests, when a user is added
as reviewer of one or more PR on one of more repositories, an icon is shown on the system tray.

## Configuration

### Auth

Create an oauth [token](https://github.com/settings/tokens) with the following permissions:

- `repo:status`

## Configuration file

Create a file named `gprmon.yml` at the same level of `gprmon.py`, example:

```yaml
---

# Optional (examples are default values)
interval: 30           # Interval between checks
always_visible: false  # By default icon is only shown when there are PRs pending to review
log_level: INFO

# Mandatory
token: "<oauth token>" # Mandatory but can be set as environment variable GITHUB_TOKEN
organization: "myorg"
url: "https://github.mydomain.com"
repos:
  - "repo1"
  - "repo2"
match: "user_login_name"
```
