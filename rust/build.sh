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
fi
