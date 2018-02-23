#!/usr/bin/env python

"""
This script allows to identify old repositories on a Github organization and
archive them locally.
"""

import sys
import os
import getpass
import exceptions
import datetime
import argparse
import subprocess
import pickle

try:
    from dateutil.relativedelta import relativedelta
except exceptions.ImportError:
    print("Unable to import from dateutil module.")
    print("This program needs python-dateutil")
    print("Install using (e.g.):")
    print("  sudo apt-get install python-dateutil")
    sys.exit()

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
    parser.add_argument('-o', '--organization', dest='organization', type=str,
                        default='ethz-asl',
                        help='Github organization. Defaults to ethz-asl')
    parser.add_argument('-c', '--check-only', dest='check_only',
                        action='store_true',
                        help='only check for outdated repos (no updates in '
                        'the last year) and print list, no further action '
                        'taken (off by default)')
    parser.add_argument('-b', '--blacklist', dest='blacklist', type=str,
                        help='blacklist text file with repositories to be '
                        'archived, one by line (if set no check for outdated '
                        'repos will be done)')
    parser.add_argument('-w', '--whitelist', dest='whitelist', type=str,
                        help='whitelist text file with repositories to be '
                        'ignored, one by line (overrides items in blacklist)')
    parser.add_argument('-n', '--do-not-archive', dest='do_not_archive',
                        action='store_true',
                        help='if set, archival of flagged repos is not '
                        'performed (off by default)')
    parser.add_argument('-d', '--delete', dest='delete',
                        action='store_true',
                        help='delete flagged repos, will ask for confirmation '
                        '(off by default)')

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
        user = g.get_user()
        try:
          otp_auth = user.create_authorization(scopes=['user','repo','delete_repo'], note='otp_auth')
        except GithubException as e:
          # Unable to import TwoFactorAuthentication for some reason. Just assume anything
          # that goes wrong is due to 2fa.
          otp_key = raw_input("Enter github Two-Factor Auth key: ")
          otp_auth = user.create_authorization(scopes=['user','repo','delete_repo'], note='otp_auth', onetime_password=otp_key)

        g = Github(otp_auth.token)
        all_repos = g.get_organization(args.organization).get_repos()[:]
        repo_list = []

        if not args.blacklist or args.check_only:
            print 'Fetching outdated repos...'
            a_year_ago =  datetime.datetime.now() - relativedelta(years=1)

            print "The following repos have not been updated in the last year:"
            for repo in all_repos:
                if repo.updated_at < a_year_ago: # and repo.private:
                    print "    " + repo.name + ", last updated: " + \
                          str(repo.updated_at)
                    repo_list.append(repo.name)

            if args.check_only:
                sys.exit()
        else:
            # Get repo names from blacklist file
            with open(args.blacklist) as f:
                repo_list = [x.strip('\n') for x in f.readlines()]

        if args.whitelist:
            # Get repo names from whitelist file and filter
            with open(args.whitelist) as f:
                whitelisted = [x.strip('\n') for x in f.readlines()]
            repo_list = [x for x in repo_list if x not in whitelisted]

        print "Repos flagged for archival:"
        for r in repo_list: print "    " + r
        sys.stdout.write("\n")

        # Archive repo: clone repo, wiki, and pickle issues (into current
        # working directory)
        for r in repo_list:
            if args.do_not_archive:
                print "Repos will not be archived (-n option)"
                break

            print "Archiving " + r + "..."
            repo = g.get_organization(args.organization).get_repo(r)

            # Clone repo
            if os.path.exists(os.getcwd() + "/" + r + ".git"):
                print ("!!! Could not clone " + r + ", name already exists in "
                       "current directory.")
            else:
                ret = subprocess.call("git clone --mirror " + repo.ssh_url,
                                      shell=True)
                if ret == 0:
                    print r + " cloned successfully."
                else:
                    print "!!! Something went wrong when cloning repo."

            # Clone wiki
            # Note: looks like repo.has_wiki is always true, even if the wiki
            # repo does not exist
            if os.path.exists(os.getcwd() + "/" + r + ".wiki.git"):
                print ("!!! Could not clone " + r + "'s wiki, name already "
                       "exists in current directory.")
            else:
                ret = subprocess.call("git clone --mirror " + \
                                      repo.ssh_url[:-3] + "wiki.git", \
                                      shell=True)
                if ret == 0:
                    print r + "'s wiki cloned successfully."
                else:
                    print "!!! Unable to clone wiki repo."

            # Pickle issues
            if repo.has_issues:
                if os.path.exists(os.getcwd() + "/" + r + ".issues"):
                    print ("!!! Could not save " + r + "'s issues, name "
                           "already exists in current directory.")
                else:
                    all_issues = []
                    for issue in repo.get_issues():
                        all_issues.append(issue)
                    with open(repo.name + ".issues", 'w') as issues_file:
                        pickle.dump(all_issues, issues_file)
                    print ("Archived " + str(len(all_issues)) + " total issues"
                          " for repo " + repo.name + ".")

            print "\n" + r + " done.\n"

        if args.delete:
            # Delete archived repos on Github (asking for confirmation)
            print "The following repos are flagged for deletion on Github:"
            for r in repo_list:
                sys.stdout.write(r + " ")
            sys.stdout.write("\nDeleting a repo on Github can't be easily "
                             "undone.\n")
            answer = query_yes_no("Do you really want to delete them?")

            if answer:
                for r in repo_list:
                    repo = g.get_organization(args.organization).get_repo(r)
                    repo.delete()
                    print "Deleted " + r
            else:
                print "No Github repos have been deleted."

    except GithubException as e:
        print "Something went wrong:"
        print e
    except IOError as e:
        print "Error while dealing with file:"
        print e
