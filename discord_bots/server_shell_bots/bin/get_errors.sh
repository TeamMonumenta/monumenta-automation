#!/usr/bin/zsh

grep --text -A2 "$(date --date='-1 minute' +'%H:%M'):.*Server thread/ERROR" latest.log
grep --text -A2 "$(date +'%H:%M'):.*Server thread/ERROR" latest.log

