#!/usr/bin/env python3

from argparse import ArgumentParser, ArgumentError
from datetime import datetime, timedelta
from email.mime.text import MIMEText

import os
import sys
import ssl
import smtplib
import requests


def env_or_required(key):
    return (
        {'default': os.environ.get(key)} if os.environ.get(key)
        else {'required': True}
    )
parser = ArgumentParser(
        description="""Produces a summary of all opened, closed, and in progress
        pull requests in the last week for a given public repository & sends the
        results to a configurable email address.""",
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
                    help="""The recipient email address to be included as
                    the To: header value.""")
try:
    args = parser.parse_args()
except ArgumentError as arg_e:
    print(f'Catching an argumentError: {arg_e}')
    sys.exit(-1)


# globals
repo_owner  = args.owner
repo_name   = args.repo
repo        = f"{repo_owner}/{repo_name}"
smtp_server = args.server
smtp_port   = args.port
smtp_user   = args.username
smtp_pass   = args.password
smtp_to     = args.recipient


def to_html(results):
    """ Formats results list data as an HTML table. Extracts table
    columns from pr_data selections.
    """

    sections = ""
    pr_data = {
        "#": "number",
        "Title": "title",
        "URL": "url",
    }

    # Create table header html block. Column titles from pr_data keys
    th = ""
    for k in pr_data:
        th = th + f"<th>{k}</th>\n"
    th_block = f"""\
    <tr>
        {th}
    </tr>
    """

    # Create table data html blocks. Divide into sections for "open",
    # "in-progress", & "closed"
    for pr_type, pr_list in results.items():
        td_block = ""
        section_header = f"<h2>{pr_type} Pull Requests</h2>"

        for pr in pr_list:
            td = ""
            # add table cells
            for v in pr_data.values():
                td = td + f"<td>{pr[v]}</td>\n"
            # add table data block
            td_block = td_block + f"""\
            <tr>
                {td}
            </tr>
            """

        sections = sections + \
                """
                %s
                <table>
                    %s
                    %s
                </table>
                """ % (section_header, th_block, td_block)

    html = f"""\
    <!DOCTYPE html>
    <html>
        <head>
            <style>
                table, th, td {{
                    border: 1px solid black;
                    border-collapse: collapse;
                }}
                th, td {{
                    padding: 5px;
                    text-align: left;
                }}
            </style>
        </head>
        <body>
            {sections}
        </body>
    </html>
    """

    return html

def send_email(str_msg):
    """Sends an email over SSL using the defined SMTP server connection
    info & credentials.
    """

    msg = MIMEText(str_msg, "html")
    msg['To']      = smtp_to
    msg['From']    = smtp_user
    msg['Subject'] = f"Weekly Update: GitHub Pull Requests for {repo}"

    try:
        context = ssl.create_default_context()
        with smtplib.SMTP_SSL("smtp.gmail.com", 465, context=context) as s:
            s.login(smtp_user, smtp_pass)
            s.sendmail(smtp_user, smtp_to, msg.as_string())
            s.quit()
            print('Email sent!')
    except Exception as email_e:
        print(f'Something went wrong...: {email_e}')
        sys.exit(-1)


def get_response(state, sort, page, n):
    """Queries the GitHub REST API for pull request results."""

    token     = os.getenv('GITHUB_OAUTH_TOKEN')
    query_url = f"https://api.github.com/repos/{repo}/pulls"
    headers   = {'Authorization': f'token {token}'}
    params    = {
        "state": state,
        "sort": sort,
        "page": page,
        "per_page": n,
        "direction": "desc"
    }

    return requests.get(query_url, headers=headers, params=params)


def get_prs_postfilter():
    """Performs a query for each pr_type of pull request ("Created",
    "In Progress", "Closed") with different query parameters ("open" or
    "closed") and different sort options ("created_at" or "updated_at").

    Performs post-filtering on either the "created_at" or "updated_at"
    keys for results in the last week, depending on the pr_type of the
    query.
    """

    def pull_page(params, results, page=1, n=20, idx=1):
        results = []

        r = get_response(params[1], params[2], page, n)

        for i, pr in enumerate(r.json(), start=idx):
            pr_dt = datetime.strptime(pr[params[0]], "%Y-%m-%dT%H:%M:%SZ")
            # If date is within the last week add to results list
            if pr_dt >= datetime.now() + timedelta(days=-7):
                results.append(pr)
                # Query for next page of results if end is reached
                if i == n * page:
                    page += 1
                    idx += n
                    pull_page(params, results, page, n, idx)
        return results


    results_dict = {}
    query_map = {
        "Created": ("created_at", "open", "created"),
        "In Progress": ("updated_at", "open", "updated"),
        "Closed": ("closed_at", "closed", "updated")
    }

    # pull page for each pr_type and store results for that type
    for pr_type, query_params in query_map.items():
        results = []
        results_dict[pr_type] = pull_page(query_params, results)

    return results_dict


if __name__ == '__main__':
    try:
        send_email(to_html(get_prs_postfilter()))
    except Exception as e:
        print(e)
        sys.exit(-1)
