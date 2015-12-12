#!/usr/bin/env python

from github import Github
import sys
import os
import getpass

if __name__ == "__main__":

    if len(sys.argv) != 2:
        print "Usage: ", sys.argv[0], " username"
        sys.exit()

    username = sys.argv[1]
    password = os.environ["GITHUB_PASSWORD"]
    if not password:
        password = getpass.getpass("Enter password for %s: " % username)

    g = Github(username, password)

    print "The following repos have not been updated in the last year:"
    repos = g.get_user().get_repos()[:]
    for repo in repos:
        if repo.updated_at.year < 2015: # and repo.private:
            print repo.name, ", last updated: ", repo.updated_at
        #d = dir(repo)
        #for item in d:
        #    print item
        #sys.exit()
