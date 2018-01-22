# lab-infrastructure's Github utils

The two Python scripts in this directory allow you to download an archival copy of a Github repository
and then to restore it if needed. They also allow you to *check for outdated repositories in your organization*.
The motivation of these tools is to take old, unused repositories from Github
organizations out of the way. This is sometimes necessary, particularly in large organizations that tend to
manage a huge number of repositories.

The scripts require the Python packages `PyGithub` and `python-dateutil`.

For specifics on how to archive and restore ASL repositories, see [lab-infrastructure-private](https://github.com/ethz-asl/lab-infrastructure-private).

## github_archiver
Script to check for unused repos on a Github organization and archive them locally (removing them from Github).

Usage:
```
$ ./github_archiver.py 
usage: github_archiver.py [-h] [-o ORGANIZATION] [-c] [-b BLACKLIST]
                          [-w WHITELIST] [-n] [-d]
                          username
```

To just list outdated repositories (more than one year with no updates):
```
$ ./github_archiver.py -o your_organization -c your_username
```
This will output a list with the outdated repos. Currently the >1 year rule is hard-coded, you are welome to modify the script to make that an input argument. You can copy the output of this run to create a `blacklist.txt` file (see below).

By not passing the `-c` argument, all outdated repos will be archived locally:
```
$ ./github_archiver.py -o your_organization -b blacklist.txt -w whitelist.txt your_username
```
This will do a bare clone of all outdated repositories in `your_organization`. It will also make local copies of the associated Github wiki repositories and Github issues, that can then be restored using `github_restorer` (see below).

If `-b blacklist.txt` is provided, the repositories listed in the `blacklist.txt` file (one repository name per line) will be archived instead (this overrides checking for outdated repositories) by doing a bare clone into the current working directory.

If `-w whitelist.txt` is provided, repositories listed in `whitelist.txt` will not be archived.

Passing `-d` will delete the flagged repositories on Github after archiving them locally.

Passing `-n` has the effect of not archiving the repositories, BUT IF PASSING ALSO `-d` THEY WILL BE DELETED. This can be used to delete the flagged repositories Github (by also passing `-n`) on a second run of the script, after having archived the repositories.

So typically you would first run:
```
$ ./github_archiver.py -o your_organization -b blacklist.txt -w whitelist.txt your_username
```

and finally:
```
$ ./github_archiver.py -o your_organization -b blacklist.txt -w whitelist.txt -n -d your_username
```



## github_restorer
Script to restore a Github repo archived with the script above.

Usage:
```
$ ./github_restorer.py
usage: github_restorer.py [-h] [-o ORGANIZATION] [-f] username repository
```

Given a local copy of a repository archived with the `github_archiver` script above, living in the current working directory, you can restore the repository (including any associated Github wiki and Github issues) as follows:
```
$ ./github_restorer.py -o your_organization your_username your_repository
```
