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

if [[ ! -d "$SERVER_DIR" ]]; then
	echo "SERVER_DIR='$SERVER_DIR' does not exist!"
	exit 1
fi


args="-XX:+UnlockExperimentalVMOptions"

# If memory isn't specified, use all of the amount set by the current cgroup
if [[ "$JAVA_MEM " != " " ]]; then
	args="$args -Xmx$JAVA_MEM -Xms$JAVA_MEM"
else
	args="$args -XX:+UseCGroupMemoryLimitForHeap"
fi

# If JAVA_LARGE_PAGES variable is not empty, use hugepages
if [[ "$JAVA_LARGE_PAGES " != " " ]]; then
	args="$args -XX:LargePageSizeInBytes=2M -XX:+UseLargePages -XX:+UseLargePagesInMetaspace"
fi

# Remaining standard arguments
args="$args -XX:+UseG1GC -XX:MaxGCPauseMillis=100 -XX:+DisableExplicitGC -XX:TargetSurvivorRatio=90 -XX:G1NewSizePercent=50 -XX:G1MaxNewSizePercent=80 -XX:InitiatingHeapOccupancyPercent=10 -XX:G1MixedGCLiveThresholdPercent=50 -XX:+AggressiveOpts -XX:+AlwaysPreTouch -Dusing.aikars.flags=mcflags.emc.gs"

cd "$SERVER_DIR"
echo "Executing:"
echo java $args -jar "$JAVA_JAR"
exec java $args -jar "$JAVA_JAR"
