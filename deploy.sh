#!/bin/bash
echo "Pull Repo Down!"
ssh -t pi@192.168.7.33 "cd /home/pi/Documents/curtains; git pull; python index.py production"
echo "Deploy Done"
