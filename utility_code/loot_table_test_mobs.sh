#!/usr/bin/zsh

test_loot() (
	mark2 send -n mobs "data merge block -1018 33 -1577 {Command:\"/fill -1024 16 -1584 -1009 30 -1569 minecraft:chest{LootTable:\\\"$1\\\"} replace minecraft:brown_wool\"}"
	sleep 0.1
	mark2 send -n mobs "setblock -1017 33 -1578 minecraft:redstone_block"
	sleep 0.1
	mark2 send -n mobs "save-all"
	sleep 0.1

	./loot_table_test_mobs.py
)

if [ "$#" -ne 1 ]; then
	echo "Usage: $0 namespace:loot/table" >&2
	exit 1
fi

cd /home/rock/MCEdit-And-Automation/utility_code

mark2 send -n mobs 'forceload add -1024 -1584 -1009 -1569'
sleep 0.1

test_loot $1

mark2 send -n mobs 'forceload remove -1024 -1584 -1009 -1569'

