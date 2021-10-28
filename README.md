# git_recent_prs.py

Produces a summary of all opened, closed, and in-progress pull requests over the last week for a given public repository & sends the results to a configurable email address.


## Requirements
- Python3

## Usage
Command argments can be passed directly via the following syntax, or system environmental variables can be set to pre-populate these fields (see below examples).
### Syntax
```
usage: git_recent_prs.py [-h] [-rn REPO_NAME] [-ro REPO_OWNER] [-u USERNAME] [-p PASSWORD] [-s SERVER] [-po PORT] [-r RECIPIENT]

Produces a summary of all opened, closed, and in progress pull requests in the last week for a given public repository & sends the results
to a configurable email address.

options:
  -h, --help            show this help message and exit
  -rn REPO_NAME, --repo REPO_NAME
                        The name of the repository. (default: m3)
  -ro REPO_OWNER, --owner REPO_OWNER
                        The owner of the repository. (default: m3db)
  -u USERNAME, --username USERNAME
                        The username used for SMTP auth.
  -p PASSWORD, --password PASSWORD
                        The password used for SMTP auth.
  -s SERVER, --server SERVER
                        The SMTP server address to connect to.
  -po PORT, --port PORT
                        The port used to connect to the SMTP server.
  -r RECIPIENT, --recipient RECIPIENT
```

### Examples

#### Exporting environmental variables
##### GitHub OAuth _(optional)_
```
export GITHUB_OAUTH_TOKEN=<token>
```

##### Gmail SMTP Relay
```
export SMTP_SERVER=smtp.gmail.com
export SMTP_PORT=465
export SMTP_USER=<email>@gmail.com
export SMTP_PASS=<app_password>
export SMTP_RECIPIENT=<email>
```

#### Launching  from Docker container

```
docker run --rm -it --name python \
  -e GITHUB_OAUTH_TOKEN \
  -e SMTP_PORT \
  -e SMTP_SERVER \
  -e SMTP_USER \
  -e SMTP_PASS \
  -e SMTP_RECIPIENT \
  -v ./git_recent_prs.py:/git_recent_prs.py \
  python /git_recent_prs.py
```
