#!/usr/bin/python

import sys
import os
import getpass
import exceptions
import argparse

try:
    from github import Github, GithubException
except exceptions.ImportError:
    print("Unable to import from github module (PyGithub library).")
    print("This program needs PyGithub "
          "(http://pygithub.github.io/PyGithub/v1/index.html).")
    print("Install using (e.g.):")
    print("  easy_install PyGithub")
    print("or")
    print("  pip install PyGithub")
    sys.exit()

class Member(object):
    def __init__(self, github_nameduser):
        self.login_name = github_nameduser.login
        self.name = github_nameduser.name 
        self.email = github_nameduser.email 
        self.location = github_nameduser.location
        self.company = github_nameduser.company

        self.affiliated_organizations = list()
        for org in github_nameduser.get_orgs():
            if org.name is not None:
                name = org.name
            else:
                name = "-"
            self.affiliated_organizations.append(org.login + " [" + name + "]")

        self.access_level = github_nameduser.type
        self.last_modified = github_nameduser.last_modified

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('username', type=str,
                        help='Github username')
    parser.add_argument('-o', '--organization', dest='organization', type=str,
                        default='ethz-asl',
                        help='Github organization. Defaults to ethz-asl')
    parser.add_argument('-t', '--team', dest='team', type=str,
                        default='repo_archivers',
                        help='Github team in the organization. Defaults to repo_archivers')

    args = parser.parse_args()

    username = args.username
    if "GITHUB_PASSWORD" in os.environ:
        print "Taking password from GITHUB_PASSWORD environment variable."
        password = os.environ.get("GITHUB_PASSWORD")
    else:
        print ("GITHUB_PASSWORD environment variable is not set, so will ask "
              "for password.")
        password = getpass.getpass("Enter password for %s: " % username)

    try:
        g = Github(username, password)

        for t in g.get_organization(args.organization).get_teams():
            if t.name == args.team:
                for m in t.get_members():
                    for k in m.get_keys():
                        print k.key
                break
    except GithubException as e:
        print "Something went wrong:"
        print e
