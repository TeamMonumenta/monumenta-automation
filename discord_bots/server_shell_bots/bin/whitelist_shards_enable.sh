#!/usr/bin/zsh

enable_whitelist() (
	cd $x
	if [ -e whitelist.json.disabled ]; then
	  mv -f whitelist.json.disabled whitelist.json
	  print "Whitelist enabled for $x"
	else
	  print "Whitelist already enabled for $x"
	fi
)
for x in $@
do
	enable_whitelist $x &
done
wait
print 'Whitelists enabled for specified shards.'
