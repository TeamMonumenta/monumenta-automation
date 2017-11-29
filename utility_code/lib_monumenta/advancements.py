#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import sys

import multiprocessing as mp

from json_file import jsonFile

def renameAdvancements(worldDir,replaceList,maxProcesses=None):
    """
    If you want to rename an advancement without
    it getting removed from players, use this.

    replaceList looks like this:
    [
        ["old","new"],
        ["dungeons:yellow/find","monumenta:dungeons/yellow/find"],
        ["dungeons:yellow/complete","monumenta:dungeons/yellow/complete"],
    ]

    maxProcesses defaults to cpu count
    """
    print "Renaming advancements..."
    print "Setting up threads..."
    advancementPath = worldDir+"advancements/"

    if maxProcesses is None:
        try:
            maxProcesses = mp.cpu_count()
        except NotImplementedError:
            maxProcesses = 4

    processes = []
    queue = mp.Queue()

    for i in range(maxProcesses):
        target=_handleOneFile
        args=({
            "advDir":advancementPath,
            "queue":queue,
            "replaceList":replaceList,
        },)

        process = mp.Process(target=target, args=args)
        process.start()
        processes.append(process)

    print "Editing files in place..."
    fileList = os.listdir(worldDir+"advancements")
    fileCount = len(fileList)
    print "{}/{} queued".format(0,fileCount),
    for i in range(fileCount):
        print "\r{}/{} queued".format(i,fileCount),
        fileName = fileList[i]
        path = fileName
        queue.put(path)
    print "\r{}/{} queued".format(fileCount,fileCount)

    for i in range(maxProcesses):
        queue.put(True)

    for p in processes:
        p.join()

    print "Done!"

def _handleOneFile(arguements):
    """
    Don't run this function externally

    When called as a process, it will get file
    names to edit from the queue. It will exit
    when it gets True.
    """
    advPath = arguements["advDir"]
    queue = arguements["queue"]
    replaceList = arguements["replaceList"]

    fileName = queue.get()
    while fileName is not True:
        try:
            path = advPath + fileName
            advFile = jsonFile(path)
            for replacement in replaceList:
                old = replacement[0]
                if old in advFile.dict.keys():
                    new = replacement[1]
                    advFile.dict[new] = advFile.dict.pop(old)
            advFile.save()
        except:
            print "\r!!! Error occured with file "+fileName+"!\n"
            pass
        fileName = queue.get()

