#!/bin/bash

if [[ $# -ne 1 ]]; then
	echo "Usage: $0 <path>"
	echo "  Scans <path> for files that are non-ascii and non-UTF-8"
fi

find "$1" -type f -exec file --mime {} \; | grep -v '.git' | grep -v "charset=utf-8" | grep -v "charset=us-ascii"
