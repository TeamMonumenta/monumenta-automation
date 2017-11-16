# Run as:
# terrain_reset_step3_build.sh <beta server ip> <beta server port> <Update Daily? true/false>

# Init stuff
today=$(date +'%Y_%m_%d')
betaIP=$1
betaPort=$2
updateDaily=$3

# the most recent file matching said pattern
tutorialGood=$(ls -1 -t ~/Project_Epic-tutorial.good.*.tgz | head -n1)

################################################################################
# Start

# 1. Change to the tmp directory. You may have to clean it out by moving old junk in that folder someplace (don't delete it, just in case.)
cd ~/tmp/${today}


# 2/1. Copy the new tarball from the play server
scp -P ${betaPort} "${betaIP}:/home/rock/project_epic_pre_reset_${today}.tgz" .


# 3/1. Unpack the tarball (creates project_epic folder)
tar xzf project_epic_pre_reset_${today}.tgz


# 4/1. Rename unpacked folder
mv project_epic PRE_RESET


# 5/1. Archive the beta server tarball just in case
mv project_epic_pre_reset_${today}.tgz ~/0_OLD_BACKUPS


# 6/1. Remove the pre-reset files that are not needed
# (shouldn't these be removed before sending?)
rm -r PRE_RESET/tutorial
rm -r PRE_RESET/purgatory


################################################################################
# Bungee

# 1. Hopefully no new shards have been added. If they have been... you'll have to edit the bungeecord config manually. Otherwise you can probably just copy the bungee folder as-is
mv PRE_RESET/bungee POST_RESET/


# 2/1. Increment the version number in POST_RESET/bungee/config.yml
# Because I know I CAN write code to select that one number, but really don't WANT to.
echo "Please manually increment the version number in ~/tmp/${today}/POST_RESET/bungee/config.yml; eg:"
echo "motd: 'Monumenta : Beta 2.1   Version: 1.12.2'"
echo "\\|/"
echo "motd: 'Monumenta : Beta 2.2   Version: 1.12.2'"
echo ""
read -p "Press a key when done."


################################################################################
# Server Config Template

# 1. Go make a commit in the server config's data directory
cd ~/project_epic/server_config/data
git add .
git commit -m "Changes for terrain reset on ${today}"
cd ~/tmp/${today}

# 2/1. Copy the build server's config
cp -a ~/project_epic/server_config POST_RESET/


# 3/1. Update these things in the POST_RESET/server_config/server_config_template:
cd POST_RESET/server_config/server_config_template/
sed -i '' "s_difficulty=[0-9]*_difficulty=2_" server.properties
echo '     0    */12 *    *    *    ~backup' >> mark2-scripts.txt
sed -i '' "s_tab-complete: [0-9]*_tab-complete: 9999_" spigot.yml
cd ../../../


# 4/1. Update the server's server_version (and daily_version too if reset spans when the daily reset would be). First open the PRE_RESET version to find what the version(s) are, then increment them in the POST_RESET version DON'T SCREW THIS UP
server_version=$(($(grep "^version: " config.yml | awk '{ print $2 }') + 1))
sed -i '' "s_^version: [0-9]*_version: ${server_version}_" config.yml
if ${updateDaily}; then
    daily_version=$(($(grep "^daily_version: " config.yml | awk '{ print $2 }')+1))
    sed -i '' "s_^daily_version: [0-9]*_daily_version: ${daily_version}_" config.yml
fi


# 5/1. Copy the luckperms settings from the beta server
rm -rf POST_RESET/server_config/plugins/LuckPerms/yaml-storage
mv PRE_RESET/server_config/plugins/LuckPerms/yaml-storage POST_RESET/server_config/plugins/LuckPerms/yaml-storage


# 6/1. Server config template complete - delete the old server_config directory
rm -rf PRE_RESET/server_config


################################################################################
# Purgatory

# 1. Copy purgatory from the build server
cp -a ~/project_epic/purgatory POST_RESET/


################################################################################
# Tutorial

# 1. Extract a known-good copy of the tutorial
mkdir POST_RESET/tutorial
cd POST_RESET/tutorial
tar xzf ${tutorialGood}
cd ~/tmp/${today}


################################################################################
# Region 1, dungeons, betaplots, r1plots

# 1. Make damn sure region_1 is stopped on the build server!
mark2 send --name "bungee" "say Stopping for terrain reset!"
mark2 send --name "bungee" --wait "Thank you and goodbye" "~stop 3m;2m;1m;30s;10s"

for shard in $(mark2 list); do
    # There should really be a line saying "done" or something at the end - need to delay with this line
    { mark2 send --name "$shard" --wait "Saving chunks for level 'Project_Epic-${shard}_the_end'/the_end" "~stop" } &
done
# Wait for all threads to finish
wait
# Give a little extra time for the shard to be completely stopped
sleep 10


# 2. Modify the terrain reset script to have correct paths:
echo "Please manually modify ~/MCEdit-And-Automation/utility_code/terrain_reset.py's paths"
echo "Terrain reset working directory:"
echo "~/tmp/${today}"
read -p "Press a key when done."


# 3/1. Run the terrain reset script
~/MCEdit-And-Automation/utility_code/terrain_reset.py


# 4/1. Copy the coreprotect databases
for x in betaplots r1plots region_1; do
    mkdir -p POST_RESET/$x/plugins/CoreProtect
    mv PRE_RESET/$x/plugins/CoreProtect/database.db POST_RESET/$x/plugins/CoreProtect/database.db
    mkdir -p POST_RESET/$x/plugins/EasyWarp
    mv PRE_RESET/$x/plugins/EasyWarp/warps.yml POST_RESET/$x/plugins/EasyWarp/warps.yml
done


################################################################################
# Build shard

mv PRE_RESET/build POST_RESET/


################################################################################
# Whitelist / Opslist / Banlist

# 1. Copy the whitelist, opslist, and banlist from the play server. Overwrite if prompted
for x in betaplots lightblue magenta orange r1bonus r1plots region_1 tutorial white yellow; do
    cp -f PRE_RESET/region_1/whitelist.json POST_RESET/$x/
    cp -f PRE_RESET/region_1/banned-players.json POST_RESET/$x/
    cp -f PRE_RESET/region_1/ops.json POST_RESET/$x/
done

################################################################################
# Load appropriate configuration for each server

# 1. Set the path to include the tool:
export PATH="$PATH:$HOME/MCEdit-And-Automation/utility_code"


# 2/1. Edit the tool if necessary to make sure the config is correct for each server. TODO: Right now this doesn't have clear distinction between build and play servers
echo "Edit this tool if necessary to make sure the config is correct for each server."
echo "~/MCEdit-And-Automation/utility_code/gen_server_config.py"
read -p "Press a key when done."


# 3/1. Run it on each server
cd POST_RESET
for x in build betaplots lightblue magenta orange purgatory r1bonus r1plots region_1 tutorial white yellow; do
    gen_server_config.py $x
done
cd ..


################################################################################
# Final steps

# 1. Make sure there are no broken symbolic links
echo "Make sure there are no broken symbolic links:"
echo "*** Fix any files below here:"
find POST_RESET -xtype l
echo "*** Fix any files above here:"

# 2/1. Rename the reset directory
mv POST_RESET project_epic


# 3/1. Tar the directory
tar czf project_epic_post_reset_${date}.tgz project_epic


# 4/1. Upload it to the play server
scp -P ${betaPort} project_epic_post_reset_11_11_2017.tgz '${betaIP}:/home/rock/'


# 5/1. Back on the play server
echo "Done; Run step 4 on the play server"

