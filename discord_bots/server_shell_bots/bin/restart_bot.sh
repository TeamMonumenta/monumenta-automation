#!/usr/bin/zsh
# DO NOT RUN THIS COMMAND EXCEPT AS THE BOT
mypath=$0:A
cd $mypath

# PID of existing bot passed as arguement
bot_PID=$1
shift

# Kill it (keyboard interupt)
kill -INT $bot_PID
while [ -e "/proc/$bot_PID" ]; do
    sleep 1
done

./start_bot.sh
