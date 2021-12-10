#!/bin/bash

check_var() {
	var="$1"

	if [[ "${!var} " == " " ]]; then
		echo "${var} environment variable must be set"
		exit 1
	fi
}

check_var SERVER_DIR
check_var JAVA_JAR
check_var JAVA_MEM
check_var JAVA_META_MEM

if [[ ! -d "$SERVER_DIR" ]]; then
	echo "SERVER_DIR='$SERVER_DIR' does not exist!"
	exit 1
fi

args="-Xmx$JAVA_MEM -Xms$JAVA_MEM -XX:MaxMetaspaceSize=$JAVA_META_MEM"

# If JAVA_LARGE_PAGES variable is not empty, use hugepages
if [[ "$JAVA_LARGE_PAGES " != " " ]]; then
	args="$args -XX:LargePageSizeInBytes=2M -XX:+UseLargePages"
fi

# Remaining standard arguments
args="$args -XX:+UseG1GC -XX:+ParallelRefProcEnabled -XX:MaxGCPauseMillis=200 -XX:+UnlockExperimentalVMOptions -XX:+DisableExplicitGC -XX:+AlwaysPreTouch -XX:G1NewSizePercent=30 -XX:G1MaxNewSizePercent=40 -XX:G1HeapRegionSize=8M -XX:G1ReservePercent=20 -XX:G1HeapWastePercent=5 -XX:G1MixedGCCountTarget=4 -XX:InitiatingHeapOccupancyPercent=15 -XX:G1MixedGCLiveThresholdPercent=90 -XX:G1RSetUpdatingPauseTimePercent=5 -XX:SurvivorRatio=32 -XX:+PerfDisableSharedMem -XX:MaxTenuringThreshold=1 -Dusing.aikars.flags=https://mcflags.emc.gs -Daikars.new.flags=true -Dlog4j2.formatMsgNoLookups=true --illegal-access=permit"

cd "$SERVER_DIR"
echo "Executing:"
echo java $args -jar "$JAVA_JAR"
exec java $args -jar "$JAVA_JAR"
