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
# Remove lines with "type":
# Remove lines with "weight":
# Remove lines with "functions*":
# Remove lines with "pools":
# Remove lines with "rolls":
# Remove lines with "min":
# Remove lines with "max":
# Remove lines with "count":
# Remove lines with "entries":
# Remove empty lines
# Remove lines containing brackets but no ':' or '"' characters
# Remove everything except pairs of lines with "name": on one line and an nbt line containing display: and Name: on the next
# Replace "name" with "id" and add opening brackets
# Process the tag into two tags with appropriate brackets
# Remove the AttributeModifiers from the nbt to match
# Pull the name out of the match nbt and just match that
perl -pe 's|\\||g' "$in" | \
	perl -pe 's|^[\t ]*"(type)":.*$||g' | \
	perl -pe 's|^[\t ]*"weight":.*$||g' | \
	perl -pe 's|^[\t ]*"functions*":.*$||g' | \
	perl -pe 's|^[\t ]*"pools":.*$||g' | \
	perl -pe 's|^[\t ]*"rolls":.*$||g' | \
	perl -pe 's|^[\t ]*"min":.*$||g' | \
	perl -pe 's|^[\t ]*"max":.*$||g' | \
	perl -pe 's|^[\t ]*"count":.*$||g' | \
	perl -pe 's|^[\t ]*"entries":.*$||g' | \
	sed -e '/^[ \t]*$/d' | \
	perl -pe 's|^[^:"]*[{}\[\]][^:"]*$||g' | \
	pcregrep -M '"name":.*\n.*display:.*Name:' | \
	perl -pe 's|[^t ]*"name".*("[^"]*")|\t[\n\t\t{\n\t\t\t"id":\1|g' | \
	perl -pe 's|^.*"tag"[^"]*"(.*)"$|\t\t\t"nbt":ur'"'''\1'''"'\n\t\t},\n\t\t[\n\t\t\t"nbt", "replace", ur'"'''\1'''"'\n\t\t]\n\t],|g' | \
	perl -pe 's|^([\t ]*"nbt":ur.*)AttributeModifiers:\[[^\]]*|\1|g' | \
	perl -pe 's|^([\t ]*"nbt":ur).*(Name:"[^"]*").*$|\1'"'''"'{display:{\2}}'"'''"'|g' > "$out"

echo "Done" >&2

