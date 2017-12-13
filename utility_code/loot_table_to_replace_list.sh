#!/bin/bash

if [[ $# -ne 1 ]] && [[ $# -ne 2 ]]; then
	echo "Usage: $0 <path/to/loot_table.json> [path/to/replace.txt]"
	echo " Empty output replace file uses stdout"
	exit 1
fi

in="$1"
out="$2"

if [[ " $out" == " " ]]; then
	out="/dev/stdout"
fi

if [[ ! -f "$in" ]]; then
	echo "Input file '$in' does not exist"
	exit 1
fi

if [[ -e "$out" ]] && [[ "$out" != "/dev/stdout" ]]; then
	echo "Stubbornly refusing to clobber output file '$out'"
	exit 1
fi

# Remove backslashes
# Remove lines with "(type|weight|functions|pools|rolls|min|max|count|entries)":
# Remove lines with "minecraft:[a-z_]*_potion":
# Remove empty lines
# Remove lines containing brackets but no ':' or '"' characters
# Remove everything except pairs of lines with "name": on one line and an nbt line containing display: and Name: on the next
# Replace "name" with "id" and add opening brackets
# Process the tag into two tags with appropriate brackets
# Remove the AttributeModifiers from the nbt to match
# Pull the name out of the match nbt and just match that
# Match just the name, not the NBT name
perl -pe 's|\\||g' "$in" | \
	grep -vE '^\s*"(type|weight|functions|function|pools|rolls|min|max|count|entries)":' | \
	grep -vi 'minecraft:[a-z_]*potion' | \
	sed -e '/^\s*$/d' | \
	perl -pe 's|^[^:"]*[{}\[\]][^:"]*$||g' | \
	pcregrep -M '"name":.*\n.*display:.*Name:' | \
	perl -pe 's|[^t ]*"name".*("[^"]*")|\t[\n\t\t{\n\t\t\t"id":\1|g' | \
	perl -pe 's|^.*"tag"[^"]*"(.*)"$|\t\t\t"nbt":ur'"'''\1'''"'\n\t\t},\n\t\t[\n\t\t\t"nbt", "replace", ur'"'''\1'''"'\n\t\t]\n\t],|g' | \
	perl -pe 's|^(\s*"nbt":ur.*)AttributeModifiers:\[[^\]]*|\1|g' | \
	perl -pe 's|^(\s*"nbt":ur).*(Name:"[^"]*").*$|\1'"'''"'{display:{\2}}'"'''"'|g' | \
	perl -pe 's|"nbt":ur'"'''"'\{display:\{Name:"(§[a-z0-9])*([^,}"]*)".*$|"name":u'"'''"'\2'"'''"',|g' > "$out"

echo "Done" >&2
