#!/usr/bin/zsh

launch_server() (
	cd $x
	mark2 start > /dev/null
	print "Finished starting $x"
)
for x in $@
do
	launch_server $x &
done
wait
print 'All shards should be started. Please verify.'
