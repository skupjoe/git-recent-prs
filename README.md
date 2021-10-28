# git-recent-prs
Produces a summary of all opened, closed, and in-progress pull requests over the last week for a given public repository & sends the results to a configurable email address.

## Requirements
- Python3 or Docker

## Usage
Command arguments can be passed directly via the following syntax, or system environmental variables can be set to pre-populate these fields (see below examples).

### Syntax
The basic command line syntax is as follows:
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
Environmental variables can be set instead of command line arguments. The current supported environmental variables are listed below.

##### GitHub OAuth _(optional)_
A GitHub OAuth token may be defined to access private repositories and unlock a higher rate-limit for requests.
```
export GITHUB_OAUTH_TOKEN=<token>
```

##### Gmail SMTP Relay
Gmail users can use Gmail's SMTP server as a relay for emails by defining similar settings as below:
```
export SMTP_SERVER=smtp.gmail.com
export SMTP_PORT=465
export SMTP_USER=<email>@gmail.com
export SMTP_PASS=<app_password>
export SMTP_RECIPIENT=<email>
```

#### Launching  from Docker container
A Docker container environment can be used to quickly launch Python3 without installing any extra dependencies.
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
