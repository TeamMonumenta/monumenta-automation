#!/usr/bin/zsh
# Start the bot and its screen session
mydir=${0:a:h}
cd $mydir

# Create screen session if it does not exist
if ! screen -list | grep -q "bot"; then
    screen -dmS bot
fi

# Start bot in screen session
screen -S bot -X stuff "$mydir/start_bot_internal.sh $@\n"
