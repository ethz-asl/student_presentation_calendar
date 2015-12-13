#!/usr/bin/env python

import sys
import os
import getpass

try:
    from github import Github, GithubException
except Exception:
    print("Unable to import github module (from PyGithub library).")
    print("This program needs PyGithub (http://jacquev6.net/PyGithub/v1/introduction.html).")
    print("Install using (e.g.):")
    print("  easy_install PyGithub")
    print("or")
    print("  pip install PyGithub")
    sys.exit()

if __name__ == "__main__":

    if len(sys.argv) != 2:
        print "Usage: " + sys.argv[0] + " username"
        sys.exit()

    username = sys.argv[1]
    if "GITHUB_PASSWORD" in os.environ:
        print "Taking password from GITHUB_PASSWORD environment variable."
        password = os.environ.get("GITHUB_PASSWORD")
    else:
        print "GITHUB_PASSWORD environment variable is not set."
        password = getpass.getpass("Enter password for %s: " % username)

    try:
        g = Github(username, password)
        repos = g.get_user().get_repos()[:]
        
        print "The following repos have not been updated in the last year:"
        for repo in repos:
            if repo.updated_at.year < 2015: # and repo.private:
                print repo.name + ", last updated: " + str(repo.updated_at)
            #d = dir(repo)
            #for item in d:
            #    print item
            #sys.exit()
                
    except GithubException as e:
        print "Something went wrong:"
        print e