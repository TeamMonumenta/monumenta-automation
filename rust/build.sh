#!/bin/bash

rm -rf bin
cargo build --release
if [[ $? -eq 0 ]]; then
	mkdir bin

	echo
	for file in src/bin/*.rs; do
		fname="$(basename $file | perl -p -e 's|\.rs$||g')"
		mv "target/release/$fname" bin/
	done
	tree bin

	if [ -d "/home/epic/4_SHARED/lockouts" ]; then
		rm /home/epic/4_SHARED/lockouts/lockout
		cp -a bin/lockout /home/epic/4_SHARED/lockouts/
	fi
fi
