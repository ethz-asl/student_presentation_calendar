#!/bin/bash

sudo apt-get install aha colordiff

DIR=$(dirname $0)

sudo ln -nsv $DIR /root/megacli-monitor
sudo cp -i megacli-cron /etc/cron.d/

