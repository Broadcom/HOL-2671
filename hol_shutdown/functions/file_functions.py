import json
import os
import re
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

debug = False

# File & Folder Functions

def createFile(newFile, content):
    print(f"TASK: Create File: {newFile}")
    if not os.path.isfile(newFile):
        print(f"INFO: File: {newFile} does not exist.")
        with open(newFile, "w") as f:
            f.write(content)
            print(f"INFO: File: {newFile} created.")
    else:
        print(f"INFO: File: {newFile} already exists.")
        print(f"TASK: Removing old version of {newFile}.")
        os.remove(newFile)

        with open(newFile, "w") as f:
            print(f"INFO: New Created: {newFile}.")
            f.write(content)

def createFolder(folder):
    try:
        if not os.path.exists(folder):
            os.makedirs(folder)
            print(f"INFO: Folder {folder} created successfully.")
        else:
            print(f"INFO: Folder {folder} already exists.")
    except Exception as e:
        raise SystemExit(f"ERROR: {e}.")

def checkFolder(folder):
    print(f"TASK: Create Folder: {folder}")
    if os.path.exists(folder):
        print(f"INFO: Folder: {folder} already exists." )
        return True 
    else:
        print(f"INFO: Folder: {folder} does not exist." )
        return False

def checkFile(aFile):
    print(f"TASK: Checking {aFile} exists.")
    if not os.path.isfile(aFile):
        print(f"INFO: File: {aFile} not found.")
        return False
    else:
        print(f"INFO: File: {aFile} found.")
        return True

def deleteFile(aFile):
    print(f"TASK: Delete File: {aFile}")
    if os.path.isfile(aFile):
        print(f"INFO: Deleting File: {aFile}.")
        os.remove(aFile)
    else:
        print(f"INFO: File: {aFile} does not exist.")

def deleteFolder(folder): 
    print(f"TASK: Delete Folder: {folder}")
    if os.path.exists(folder):
        print(f"INFO: Deleting Folder: {folder}.")
        os.rmdir(folder)
    else:
        print(f"INFO: Folder: {folder} does not exist.")

def readFile(aFile):
    if not os.path.exists(aFile):
        raise Exception(f"INFO: {aFile} not found")
    else:
        with open(aFile, "r") as f:
            return f.read().strip()

