# Run as:
# step4_beta.sh <Ops only? true/false>


# Init stuff
today = $(date +'%Y_%m_%d')

opsOnly=$1

################################################################################
# Back on the play server

# 1. Unpack the tarball
tar xzf project_epic_post_reset_${date}.tgz

# 2/1. If you were following along, the project_epic directory was already archived somewhere safe. If not, do so now.
# Nick: Wait, didn't we leave off in the home directory? Didn't we just extract to the final destination?


# 3/1. Move the backup directory back
# Nick: ???
# Nick: This isn't the post-reset world, is it?
mv ~/tmp/backups/ ~/project_epic/

# 4/1. Go to each shard (EXCEPT BUNGEE!) and start them using mark2 start
for x in betaplots lightblue magenta orange r1bonus r1plots region_1 tutorial white yellow build; do
    cd ~/project_epic/$x
    if opsOnly; then
        mv whitelist.json whitelist.json.bak
    fi
    { mark2 start } &
done
wait
# All the shards should be up by this point


# 5/1. Use mark2 attach to verify that each and every server is up and running
mark2 attach


# 6/1. Finally, start bungeecord.
cd ~/project_epic/bungee
mark2 start


