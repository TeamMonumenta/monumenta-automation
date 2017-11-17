# Init stuff
today=$(date +'%Y_%m_%d')

################################################################################
# Start

# 1. Log onto the beta server.


# 2. mark2 attach, switch to bungee and run ~stop 10m;5m;3m;2m;1m;30s;10s

# Request for Bungee to halt
mark2 send --name "bungee" --wait "Thank you and goodbye" "~stop 10m;5m;3m;2m;1m;30s;10s"


# 3. Once bungee shuts down, ~stop all the other shards
# - simple multithreading to speed up shutdown proceedure
for shard in $(mark2 list); do
    # There should really be a line saying "done" or something at the end - need to delay with this line
    { mark2 send --name "$shard" --wait "Saving chunks for level 'Project_Epic-${shard}_the_end'/the_end" "~stop" } &
done
# Wait for all threads to finish
wait

# Might be possible to use this instead?
#mark2 sendall --wait "Saving chunks for level 'Project_Epic-*_the_end'/the_end" "~stop"

# Add just a bit more delay for the shards to properly stop (still saving on last printed line)
sleep 10
# Ok, maybe more delay than needed, but less delay than watching TV and coming back in half an hour.


# 4. Move the backups directory out of the way for now
mv ~/project_epic/backups ~/tmp/


# 5/1. Tarball the whole project_epic folder once everything is stopped as a backup
# From here forth, I use a / to denote the messed up numbering on the blog;
# it amused me. Nothing we can do about it because of the multiline code blocks.
cd ~
tar czf project_epic_pre_reset_full_backup_${today}.tgz project_epic


# 6/1. Since the dungeon region files are giant and no longer needed, delete them and re-tarball the thing for faster transferring.
cd ~/project_epic
for x in white orange magenta lightblue yellow r1bonus tutorial purgatory; do
    ls $x/Project_Epic-$x/region
    rm -r $x/Project_Epic-$x/region
    rm -rf $x/plugins/CoreProtect
done


# 7/1. Remove the giant spigot jars from the server_config directory
rm server_config/*.jar


# 8/1.Re-tarball the project for transferring to the build server
cd ~
tar czf project_epic_pre_reset_${today}.tgz project_epic


# 9/1. Archive the project_epic directory for later
mv project_epic ~/0_OLD_BACKUPS/project_epic_pre_reset_${today}

echo "Done; Run step 3 on the build server"

