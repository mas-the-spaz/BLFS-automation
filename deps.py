import sys
import argparse
import json
import os

errors = ["Dependencies.json not found! Try running bootstrap.py to rebuild dependency database", "no dependencies found for "]

'''
flags 
    list or DOWNLOAD?
    -l --list

    include recommneded and optional?
    -r --recommended, -o --optional

    list commands (possibly output to shell) or NORMAL (download)
    -c --commands 

    package <name>  REQUIRED
    -p --package


main function
 
output specific order of installation 
check if ftp is only link - if yes download
check if package is already downloaded
check if inputed package not exist

'''
if not os.path.exists('dependencies.json'):
    print(errors[0])
    exit

with open('dependencies.json', 'r+') as scheme:
    print(scheme[sys.argv[1]])