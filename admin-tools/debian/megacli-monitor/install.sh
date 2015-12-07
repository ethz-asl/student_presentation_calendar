#!/bin/bash

sudo apt-get install aha colordiff realpath

DIR=$(realpath $(dirname ${BASH_SOURCE[0]}))

sudo ln -nsiv $DIR /root/megacli-monitor
sudo cp -vi megacli-cron /etc/cron.d/

