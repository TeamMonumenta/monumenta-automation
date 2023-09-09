#!/usr/bin/env pypy3

import sys
import os
import json

def main():
    if len(sys.argv) == 1:
        print("Usage: python ./fixadvancements.py <input dir> <output dir>")
        return

    if len(sys.argv) < 2:
        print("Please specify the input directory as the first argument.")
        return

    inputPath = sys.argv[1]

    if len(sys.argv) < 3:
        print("Please specify the output directory as the second argument.")
        return

    outputPath = sys.argv[2]

    try:
        print("Attempting to fix {} advancement files found in the directory at {}, and outputting to {}".format(len(os.listdir(inputPath)), inputPath, outputPath))
    except Exception:
        print("At least one of the specified paths is invalid.")
        return

    fileNames = os.listdir(inputPath)
    for fileName in fileNames:
        # Skip non-json files
        if not fileName.endswith(".json"):
            continue

        filePath = "{}/{}".format(inputPath, fileName)
        with open(filePath) as currentFile:
            advancementData = json.load(currentFile)

        # Remove any key that starts with "minecraft"
        for k in list(advancementData.keys()):
            if k.startswith("minecraft"):
                del advancementData[k]

        # Create the specified output directory if it doesn't already exist.
        if not os.path.exists(outputPath):
            os.makedirs(outputPath)

        fileOutputPath = "{}/{}".format(outputPath, fileName)
        with open(fileOutputPath, "w") as outFile:
            json.dump(advancementData, outFile)

if __name__ == "__main__":
    main()
