#!/usr/bin/env python3

from argparse import ArgumentParser, ArgumentError
from datetime import datetime, timedelta
from email.message import EmailMessage

import os
import smtplib
import requests


def env_or_required(key):
    return (
        {'default': os.environ.get(key)} if os.environ.get(key)
        else {'required': True}
    )
parser = ArgumentParser(
        description="""Produces a summary of all opened, closed, and in progress pull requests in
        the last week for a given public repository & sends the results to a configurable email
        address.""",
        exit_on_error=False
)
parser.add_argument(
                    '-rn', '--repo',
                    metavar='REPO_NAME',
                    default='m3',
                    help='The name of the repository. (default: %(default)s)')
parser.add_argument(
                    '-ro', '--owner',
                    metavar='REPO_OWNER',
                    default='m3db',
                    help='The owner of the repository. (default: %(default)s)')
parser.add_argument(
                    '-u', '--username',
                    metavar='USERNAME',
                     **env_or_required('SMTP_USER'),
                    help='The username used for SMTP auth.')
parser.add_argument(
                    '-p', '--password',
                    metavar='PASSWORD',
                     **env_or_required('SMTP_PASS'),
                    help='The password used for SMTP auth.')
parser.add_argument(
                    '-s', '--server',
                    metavar='SERVER',
                     **env_or_required('SMTP_SERVER'),
                    help='The SMTP server address to connect to.')
parser.add_argument(
                    '-po', '--port',
                    metavar='PORT',
                     **env_or_required('SMTP_PORT'),
                    help='The port used to connect to the SMTP server.')
parser.add_argument(
                    '-r', '--recipient',
                    metavar='RECIPIENT',
                     **env_or_required('SMTP_RECIPIENT'),
                    help="""The recipient email address to be included as the
                    To: header value.""")
try:
    args = parser.parse_args()
except ArgumentError as arg_e:
    print(f'Catching an argumentError: {arg_e}')
    exit(-1)

# arg vars
repo_name   = args.repo
repo_owner  = args.owner
smtp_server = args.server
smtp_port   = args.port
smtp_user   = args.username
smtp_pass   = args.password
smtp_to     = args.recipient


def send_email(body, repo=f'{repo_owner}/{repo_name}'):
    """Send an email over SSL using the defined SMTP server connection info & credentials."""

    msg = EmailMessage()

    msg['To']      = smtp_to
    msg['From']    = smtp_user
    msg['Subject'] = f"Weekly Update: GitHub Pull Requests for {repo}"
    msg.set_content(body)

    try:
        s = smtplib.SMTP_SSL(smtp_server, smtp_port)
        s.login(smtp_user, smtp_pass)
        s.send_message(msg)
        s.quit()
        print('Email sent!')
    except Exception as email_e:
        print(f'Something went wrong...: {email_e}')

def get_response(state, page, sort, n):
    """Query the GitHub REST API for pull request results."""

    token     = os.getenv('GITHUB_OAUTH_TOKEN')
    query_url = f"https://api.github.com/repos/{repo_owner}/{repo_name}/pulls"
    headers   = {'Authorization': f'token {token}'}
    params    = {
        "state": state,
        "per_page": n,
        "page": page,
        "sort": sort,
        "direction": "desc"
    }
    return requests.get(query_url, headers=headers, params=params)


def get_prs_postfilter():
    """Perform a query for each type of pull request ("Created", "In Progress", "Closed") with
    different query parameters ("open" or "closed") and different sort options ("created_at" or
    "updated_at").

    Perform post-filtering on either "created_at" or "updated_at" for results in the last 7 days,
    depending on query type.
    """

    results = ""

    def pull_page(m, results=results, page=1, n=20, idx=1):
        r = get_response(m[0], page, m[2], n)

        for i, pr in enumerate(r.json(), start=idx):
            pr_dt = datetime.strptime(pr[m[1]], "%Y-%m-%dT%H:%M:%SZ")
            # If date is within the last week
            if pr_dt >= datetime.now() + timedelta(days=-7):
                # Add to results list
                results = results + "Request: #{} - {} \n{} Time: {}\n\n".format(
                    pr["number"], pr["title"], pr_type, pr[m[1]]
                )
                # Query for next page of results if end is reached
                if i == n*page:
                    page += 1
                    idx += n
                    pull_page(m, results, page, n, idx)

        return results

    query_map = {
        "Created": ("open", "created_at", "created"),
        "In Progress": ("open", "updated_at", "updated"),
        "Closed": ("closed", "closed_at", "updated")
    }
    for pr_type, pr_params in query_map.items():
        results = results + f"*{pr_type} Pull Requests*\n"
        results = results + pull_page(pr_params) + '\n'

    return results

if __name__ == '__main__':
    try:
        send_email(get_prs_postfilter())
    except Exception as e:
        print(e)
