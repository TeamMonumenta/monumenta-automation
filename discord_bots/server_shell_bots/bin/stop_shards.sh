#!/usr/bin/zsh

stop_server() (
	mark2 stop -n $x
)
for x in $@
do
	stop_server $x &
done
wait
print 'All shards should be started. Please verify.'
