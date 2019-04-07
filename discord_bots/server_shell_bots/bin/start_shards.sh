#!/usr/bin/zsh

launch_server() (
	cd "$1"
	mark2 start > /dev/null
	print "Finished starting $1"
)

for x in $@
do
	launch_server $x &
	sleep 5
done

wait
print 'All shards should be started. Please verify.'
