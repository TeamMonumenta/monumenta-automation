# Run as:
# beta_ops_only <true/false>
opsOnly=$1

ops_only_shard(){ #set to ops only or not
    shard=$1
    opsOnly=$2
    
    # stop the shard;
    # hold/unhold might work, but it would be
    # harder to tell when the shards are back up
    mark2 send --name "$shard" --wait "Thank you and goodbye" "~stop"
    
    # update the whitelist file
    cd ~/project_epic/$shard
    if $opsOnly; then
        # don't clobber existing whitelist.json.bak
        mv -n whitelist.json whitelist.json.bak
    else
        # do clobber, or whitelist.json will be empty
        mv -f whitelist.json.bak whitelist.json
    fi
    
    # start the shard
    mark2 start
}

mark2 send --name "bungee" --wait "Thank you and goodbye" "~stop"

# stop each shard, update the whitelist file, and restart.
for x in betaplots lightblue magenta orange r1bonus r1plots region_1 tutorial white yellow build; do
    ops_only_shard($x,$opsOnly) &
done
wait
sleep 10


# All the shards should be up by this point
cd ~/project_epic/bungee
mark2 start

