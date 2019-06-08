#! /usr/bin/env python3
import os
import sys
import json

if len(sys.argv) != 4:
	print('Usage: merge-json "/path/to/first/directory/" "/path/to/second/directory/" "/path/to/output/directory"')
	exit(1)

input1,input2,output = sys.argv[1:]

if os.path.isdir(input1) is False or os.path.isdir(input2) is False or os.path.isdir(input2) is False:
	print('Usage: merge-json "/path/to/first/directory/" "/path/to/second/directory/" "/path/to/output/directory"')
	exit(1)

files = {} # {"file1":("input1/file1","input2/file1", "output/file1"),"file2":("input1/file2","input2/file2", "output/file2")}

for f in os.listdir(input1):
	if f.endswith(".json"):
		if f in files:
			files[f] = (os.path.join(input1,f), files[f][1], files[f][2])
		else:
			files[f] = (os.path.join(input1,f),None,os.path.join(output,f))
for f in os.listdir(input2):
	if f.endswith(".json"):
		if f in files:
			files[f] = (files[f][0], os.path.join(input2,f), files[f][2])
		else:
			files[f] = (None,os.path.join(input2,f),os.path.join(output,f))

for k,v in files.items():
	json1 = {}
	json2 = {}
	if v[0] is not None:
		json1 = json.load(open(v[0]))
	if v[1] is not None:
		json2 = json.load(open(v[1]))
	print("Combining '%s' and '%s' into one file in '%s'"%(v[0],v[1],output))
	json1.update(json2)
	s = json.dumps(json1, indent=2).replace("'","\\u0027")
	open(v[2],"w").write(s)

