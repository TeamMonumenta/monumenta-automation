#!/bin/bash

if [[ $# -ne 1 ]]; then
	echo "Requires file argument"
	exit 1
fi

perl -p -i -e 's|(^give [^ ]* *double_plant [0-9]) .*mperial.*oin.*$|\1 0 {display:{Name:"§6§lImperial Coin",Lore:["* Special Currency *"]},ench:[{id:51,lvl:1}]}|g' "$1"

