#!/bin/bash
# make files/folders in folder $1 show up in $2 as sym links
ln -ns "$1"/.[A-Z0-9]*/ $2
ln -ns "$1"/*/ $2
cp -ans "$1"/.[A-Z0-9]* $2
cp -ans "$1"/* $2

