#!/usr/bin/zsh

cd ~/project_epic

launch_server() (
	cd $x
	mark2 start > /dev/null
	print "Finished starting $x"
)
for x in betaplots build lightblue magenta nightmare orange purgatory r1bonus r1plots region_1 roguelike tutorial white yellow
do
	launch_server $x &
done
wait
print 'All shards should be started. Please verify.'
