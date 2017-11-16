# init stuff
today=$(date +'%Y_%m_%d')

# the most recent file matching said pattern
dungeonTemplate=$(ls -1 -t ~/dungeon_template-keep-this*.tgz | head -n1)

# Find the directory the script (and server) reside in...
# http://stackoverflow.com/questions/59895/can-a-bash-script-tell-what-directory-its-stored-in
SOURCE="${BASH_SOURCE[0]}"
while [ -h "$SOURCE" ]; do # resolve $SOURCE until the file is no longer a symlink
  DIR="$( cd -P "$( dirname "$SOURCE" )" && pwd )"
  SOURCE="$(readlink "$SOURCE")"
  [[ $SOURCE != /* ]] && SOURCE="$DIR/$SOURCE" # if $SOURCE was a relative symlink, we need to resolve it relative to the path where the symlink file was located
done
DIR="$( cd -P "$( dirname "$SOURCE" )" && pwd )"

# If you're not using symlinks - and if you don't know, you probably aren't - then this one liner would be faster
# DIR=$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )

mkdir -p ~/tmp/${today}

################################################################################
# Start

# 1. Make a copy of the dungeon world folder to someplace
# -a is archive mode; copies recursively, preserves symlinks, etc
cp -a ~/project_epic/dungeon ~/tmp/${today}/Project_Epic-dungeon


# 2. Unpack the good copy of the dungeon template
cd ~/tmp/${today}
tar xzf ${dungeonTemplate}


# 3. Edit the dungeon_instance_gen.py script to update the paths and then run it. It takes around two hours. (TODO NickNackGus - update this to be MUCH faster.)
# We need to CD to the path of dungeon_instance_gen.py:
cd $DIR/..
./dungeon_instance_gen.py


# 4. Once it finishes, rename the dungeons-out folder POST_RESET (or something similar) and we’ll add things to it until the reset is done and it becomes the new beta folder.
mv ~/tmp/dungeons-out/ ~/tmp/${today}/POST_RESET/

echo "Done; Run step 2 on the play server"

