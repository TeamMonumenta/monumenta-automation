#!/usr/bin/zsh

check_whitelist() (
	cd $x
	if [ -e whitelist.json.disabled ]; then
	  print "Disabled $x"
	else
	  print "Enabled $x"
	fi
)
for x in $@
do
	check_whitelist $x &
done
wait
print 'Done.'
