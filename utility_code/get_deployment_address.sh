#!/bin/bash
ns="$1"
name="$2"

if [[ "$ns " == " " ]]
then
	echo "Usage: $0 <namespace> <name>"
	exit 1
fi

if [[ "$name " == " " ]]
then
	echo "Usage: $0 <namespace> <name>"
	exit 1
fi

addr=$(/home/epic/bin/kubectl get pods -o wide -n $ns | grep -P "$name-[0-9a-z]+-[0-9a-z]+" | awk -v X=6 '{print $X}')

if [[ "$addr " == " " ]]
then
	echo "<offline>"
	exit 1
fi
echo "$addr"
