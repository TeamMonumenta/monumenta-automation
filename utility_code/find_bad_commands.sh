#!/bin/bash

function usage(){
    echo "Usage:"
    echo "First, comment/uncomment lines from getresults() as needed"
    echo "Then, run with target files or directories"
    echo "- ~/automation/utility_code/find_bad_commands.sh example.json"
    echo "- ~/automation/utility_code/find_bad_commands.sh valley isles"
    echo "- ~/automation/utility_code/find_bad_commands.sh *"
    echo ""
    echo "Matching lines will be sorted by file location, and the first 10 lines will be displayed."
    echo "The last line shows how many matches exist for the specified patterns and files."
    echo ""
    echo "Any lines matched in ignorelines() will be filtered out. This is preferred for commands that intentionally target an entire shard with selectors."
    echo "any file names matched in ignorefiles() will be filtered out. This is preferred for ignoring files/folders, but does not improve run time."
}

function ignorelines(){
    while read data; do
        echo "$data" | grep -v '@r[a-z]' | grep -vF 'tellmini @a test' | grep -vF 'function monumenta:dungeons/brown/boss/bossbar_remove'
    done
}

function ignorefiles(){
    while read data; do
        # TODO find a time and place to be bothered by the issues in emojis folder
        # TODO remove marina from this list before launch
        # TODO remove stat_trial/hp from this list
        echo "$data" | grep -vF '.git/' | grep -vF 'souls_database.json' | grep -vF 'armor_statues/data/' | grep -vF 'futurama/data/' | grep -vF 'mobs/data/' | grep -vF 'test/data/' | grep -vP 'dev[0-9]+/data/' | grep -vP 'scriptedquests/[a-z]+/(futurama|mobs|ports|test|dev[0-9]+)/' #| grep -vF '/emojis/' #| grep -vF '/dungeons/marina/' | grep -vF '/stat_trial/hp/'
    done
}

function getresults(){
    # Find selectors with no world limit
    #grep -rIHnPe '(^|"| )@[pear][^[]' $* | ignorefiles | ignorelines
    #grep -rIHnPe '(^|"| )@[pear]\[(?![^\]]*(distance|d[xyz]|all_worlds=true)(=|\\u003d))' $* | ignorefiles | ignorelines

    # Same, but ignore @a temporarily if there's too many intendended matches.
    #grep -rIHnPe '@[per][^[]' $* | ignorefiles | ignorelines
    #grep -rIHnPe '@[per]\[(?![^\]]*(distance|d[xyz])=)' $* | ignorefiles | ignorelines

    # Match excessively large selectors (paper patch is being removed)
    #grep -rIHnPe '@[pears]\[[^\]]*distance=(\d\d\d\d+|[2-9]\d\d)' $* | ignorefiles | ignorelines

    # Redundancies TODO re-enable when distance selectors are done
    #grep -rIHnPe '@e\[[^\]]*gamemode=' $* | ignorelines
    #grep -rIHnPe '@[ea]\[[^\]]*type=(minecraft:)?player' $* | ignorelines
    #grep -rIHnPe '@[ea]\[[^\]]*sort=arbitrary' $* | ignorelines
    #grep -rIHnPe '@r\[[^\]]*sort=random' $* | ignorefiles | ignorelines
    #grep -rIHnPe '@p\[[^\]]*sort=nearest' $* | ignorefiles | ignorelines
    #grep -rIHnPe '@[pr]\[[^\]]*limit=1' $* | ignorefiles | ignorelines
    #grep -rIHnPe 'playsound .* master' $* | ignorefiles
    #grep -rIHnPe 'playsound .* @p ' $* | ignorefiles
    #grep -rIHnFe 'execute run ' $* | ignorefiles
    #grep -rIHnFe 'run {' $* | ignorefiles
    #grep -rIHnFe 'loop {' $* | ignorefiles
    #grep -rIHnFe ' run execute ' $* | ignorefiles
    #grep -rIHnFe ' run run ' $* | ignorefiles
    #grep -rIHnFe ' run loop ' $* | ignorefiles
    #grep -rIHnPe ' at @s run kill @s$' $* | ignorefiles
    #grep -rIHnFe ' as @S at @S ' $* | ignorefiles
    #grep -rIHnPe '(?<! positioned)(?<! rotated) as @s ' $* | ignorefiles

    # Commands that probably don't need a gamemode check
    #grep -rIHnPe '(?<!monumenta UpdateStrikeChests )(?<!monumenta music play now )(?<!monumenta music play next )(?<!monumenta music cancel now )(?<!monumenta music cancel next )(?<!effect clear )(?<!effect give )(?<!tellraw )(?<!title )(?<!master )(?<!music )(?<!record )(?<!weather )(?<!block )(?<!hostile )(?<!neutral )(?<!player )(?<!ambient )(?<!voice )(?<!force )(?<!normal )@[par]\[(?![^\]]*gamemode=)(?!.* function monumenta:mechanisms/music/)(?!.* function monumenta:dungeons/brown/objectives/music)(?!.* function monumenta:dungeons/gallery/easter_egg/sound)(?!.* monumenta:dungeons/gallery/easter_egg/altar_sound)' $* | ignorefiles | ignorelines

    # Replace magic block check

    #if block -1441 2 -1441 air
    #if block -1441 2 -1441 minecraft:air
    #unless block -1441 2 -1441 gold_block
    #unless block -1441 2 -1441 minecraft:gold_block
    # |
    # V
    #if score $IsPlay const matches 1

    #if block -1441 2 -1441 gold_block
    #if block -1441 2 -1441 minecraft:gold_block
    #unless block -1441 2 -1441 air
    #unless block -1441 2 -1441 minecraft:air
    # |
    # V
    #if score $IsPlay const matches 0

    #grep -rIHnF -- '-1441 2 -1441' $* | ignorefiles

    # 1.19 changes

    # CatType is now a string ID instead of a number
    # 
    #grep -rIHnP 'CatType: *\d'

    # Block/item tag #carpets -> #wool_carpets
    grep -rIHnP '#(minecraft:)?carpets' $*
}

if [ "$#" = "0" ]; then
    usage
    exit 1
fi
# TODO re-enable when distance selectors are done
getresults $* | sort -V | uniq #| head
#echo ''
#getresults $* | sort -V | uniq | wc -l
