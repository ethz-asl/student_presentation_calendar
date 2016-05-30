#!/usr/bin/env python

"""
This script allows to restore repos archived with the github_archiver
script.
"""

import sys
import os
import getpass
import exceptions
import argparse
import subprocess
import pickle

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

def query_yes_no(question, default="yes"):
    """Ask a yes/no question via raw_input() and return their answer.

    "question" is a string that is presented to the user.
    "default" is the presumed answer if the user just hits <Enter>.
        It must be "yes" (the default), "no" or None (meaning
        an answer is required of the user).

    The "answer" return value is True for "yes" or False for "no".
    """
    valid = {"yes": True, "y": True, "ye": True,
             "no": False, "n": False}
    if default is None:
        prompt = " [y/n] "
    elif default == "yes":
        prompt = " [Y/n] "
    elif default == "no":
        prompt = " [y/N] "
    else:
        raise ValueError("invalid default answer: '%s'" % default)

    while True:
        sys.stdout.write(question + prompt)
        choice = raw_input().lower()
        if default is not None and choice == '':
            return valid[default]
        elif choice in valid:
            return valid[choice]
        else:
            sys.stdout.write("Please respond with 'yes' or 'no' "
                             "(or 'y' or 'n').\n")

if __name__ == "__main__":

    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('username', type=str,
                        help='Github username')
    parser.add_argument('repository', type=str,
                        help='name of the repository to be restored')
    parser.add_argument('-o', '--organization', dest='organization', type=str,
                        default='ethz-asl',
                        help='Github organization. Defaults to ethz-asl')
    parser.add_argument('-f', '--force', dest='force',
                        action='store_true',
                        help='overwrite the Github repo if one exists already'
                        ' (DANGEROUS). Off by default.')

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

        # Assuming for now script runs in same folder where repo is archived

        # Check for backup and repo existence, wiki repo, and issues
        if not os.path.exists(os.getcwd() + "/" + args.repository + ".git"):
            print("Could not find repo directory in current working directory:"
                  " " + args.repository + ".git")
            sys.exit(1)

        try:
            g.get_organization(args.organization).get_repo(args.repository)
            if args.force:
                print "--force not implemented yet."
                sys.exit(1)
            else:
                print ("Repository '" + args.repository + "' already exists on "
                       "Github.")
                sys.exit(1)
        except GithubException as e:
            pass

        repo_has_wiki = os.path.exists(os.getcwd() + "/" + args.repository + \
                        ".wiki.git")

        # Restoring. First create repo
        repo = g.get_organization(args.organization).create_repo(\
               args.repository, private=True, has_wiki=repo_has_wiki)

        # Push
        ret = subprocess.call("cd " + args.repository + ".git && git push",
                              shell=True)
        if ret == 0:
            print "Pushed to repo [" + args.repository + "] successfully."
        else:
            print "!!! Unable to push to repo [" + args.repository + "]"

        # Restore wiki, if any
        if repo_has_wiki:
            # Create wiki repo
            #...
            # Push to wiki repo
            ret = subprocess.call("cd " + args.repository + ".wiki.git && git push",
                                  shell=True)
            if ret == 0:
                print "Pushed to repo [" + args.repository + ".wiki] successfully."
            else:
                print "!!! Unable to push to repo [" + args.repository + ".wiki]"

        # Restore issues, if any
        issues = None
        if os.path.isfile(os.getcwd() + "/" + args.repository + ".issues"):
            with open(args.repository + ".issues") as f:
                issues = pickle.load(f)
        if issues:
            for i in issues:
                print "Restoring issue: " + i.title
                #print i.body
                #print i.state
                #print i.milestone
                #print i.labels
                #sys.stdout.write('\n\n')
                repo.create_issue(i.title, body=i.body)

        print "Done."

    except GithubException as e:
        print "Something went wrong:"
        print e
    except IOError as e:
        print "Error while dealing with file:"
        print e
