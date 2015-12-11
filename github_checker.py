#!/usr/bin/env python

from github import Github
import sys

if __name__ == "__main__":

    if len(sys.argv) != 3:
        print "Usage: ", sys.argv[0], " username password"
        sys.exit()
    
    g = Github(sys.argv[1], sys.argv[2])
        
    print "The following repos have not been updated in the last year:"
    repos = g.get_user().get_repos()[:]
    for repo in repos:
        if repo.updated_at.year < 2015: # and repo.private:
            print repo.name, ", last updated: ", repo.updated_at
        #d = dir(repo)
        #for item in d:
        #    print item
        #sys.exit()        
