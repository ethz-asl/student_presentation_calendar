# lab-infrastructure's Github utils

The two Python scripts in this directory allow you to download an archival copy of a Github repository
and then to restore it if needed. The motivation of these tools is to take old, unused repositories from Github
organizations out of the way. This is sometimes necessary, particularly in large organizations that tend to
manage a huge number of repositories.

**github_archiver**
  Script to check for unused repos on a Github organization and archive them locally (removing them from Github).

**github_restorer**
  Script to restore a Github repo archived with the script above.
