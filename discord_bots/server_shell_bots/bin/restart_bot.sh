#!/usr/bin/zsh
# DO NOT RUN THIS COMMAND EXCEPT AS THE BOT
mydir=${0:a:h}
cd $mydir

# PID of existing bot passed as arguement
bot_PID=$1

# Kill it (keyboard interupt)
kill -INT $bot_PID
while [ -e "/proc/$bot_PID" ]; do
    sleep 1
done

./start_bot.sh "$2"
