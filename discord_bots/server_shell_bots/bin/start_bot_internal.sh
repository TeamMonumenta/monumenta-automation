#!/usr/bin/zsh
# DO NOT RUN THIS YOURSELF - use start_bot.sh
unset SSH_CLIENT
unset SSH_CONNECTION
unset SSH_TTY
unset SSH_AUTH_SOCK

mypath=$0:A
cd "$mypath/.."

# Pass all arguments to bot
./bot.py $@
