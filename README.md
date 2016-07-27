# lab-infrastructure

This repository contains useful scripts and tools for maintaining a robotics lab infrastructure, particularly at ETHZ's ASL.

At the moment it contains: 

- github/**github_archiver**:
  Script to check for unused repos on a Github organization and archive them locally (removing them from Github). [Learn more...](./github/)

- github/**github_restorer**:
  Script to restore a Github repo archived with the script above. [Learn more...](./github/)

- **student_presentation_calendar**:
  Extract student presentation dates from excelsheets and upload them to a google calendar.

For instructions on the internal usage of these scripts at [ASL](http://asl.ethz.ch) to archive and restore ASL repositories, see [lab-infrastructure-private](https://github.com/ethz-asl/lab-infrastructure-private).
