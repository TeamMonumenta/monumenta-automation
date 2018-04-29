#!/usr/bin/zsh

disable_whitelist() (
	cd $x
	if [ -e whitelist.json.disabled ]; then
	  print "Whitelist already disabled for $x"
	else
	  mv -f whitelist.json whitelist.json.disabled
	  print "Whitelist disabled for $x"
	fi
)
for x in $@
do
	disable_whitelist $x &
done
wait
print 'Whitelists disabled for specified shards.'
