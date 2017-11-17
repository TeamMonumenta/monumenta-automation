#!/bin/bash

if [[ $# -ne 2 ]]; then
	echo "Usage: $0 <path/to/loot_table.json> <path/to/replace.txt>"
	exit 1
fi

in="$1"
out="$2"

if [[ ! -f "$in" ]]; then
	echo "Input file '$in' does not exist"
	exit 1
fi

if [[ -e "$out" ]]; then
	echo "Stubbornly refusing to clobber output file '$out'"
	exit 1
fi

# Remove backslashes
# Remove lines with "type":
# Remove lines with "weight":
# Remove lines with "function(s)?":
# Remove empty lines
# Remove lines containing brackets but no ':' or '"' characters
# Replace "name" with "id" and add opening brackets
# Process the tag into two tags with appropriate brackets
# Remove the AttributeModifiers from the nbt to match
# Pull the name out of the match nbt and just match that
perl -pe 's|\\||g' "$in" | \
	perl -pe 's|^.*"type":.*$||g' | \
	perl -pe 's|^.*"weight":.*$||g' | \
	perl -pe 's|^.*"functions?":.*$||g' | \
	sed -e '/^[ \t]*$/d' | \
	perl -pe 's|^[^:"]*[{}\[\]][^:"]*$||g' | \
	perl -pe 's|[^t ]*"name".*("[^"]*")|\t[\n\t\t{\n\t\t\t"id":\1|g' | \
	perl -pe 's|^.*"tag"[^"]*"(.*)"$|\t\t\t"nbt":ur'"'''\1'''"'\n\t\t},\n\t\t[\n\t\t\t"nbt", "replace", ur'"'''\1'''"'\n\t\t]\n\t],|g' | \
	perl -pe 's|^([\t ]*"nbt":ur.*)AttributeModifiers:\[[^\]]*|\1|g' | \
	perl -pe 's|^([\t ]*"nbt":ur).*(Name:"[^"]*").*$|\1'"'''"'{display:{\2}}'"'''"'|g' > "$out"

echo "Done"

