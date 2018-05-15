#!/usr/bin/zsh
# Start the bot and its screen session
mypath=$0:A
cd $mypath

# Create screen session if it does not exist
if ! screen -list | grep -q "bot"; then
    screen -dmS bot
fi

# Start bot in screen session
screen -S bot -X stuff "$mypath/start_bot_internal.sh $@\n"
