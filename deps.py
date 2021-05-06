import sys
import argparse
import json
import os

errors = ["Dependencies.json not found! Try running bootstrap.py to rebuild dependency database",
          "no dependencies found for (package arguments)"]

'''
flags 
    list or DOWNLOAD?
    -l --list

    include recommended and optional?
    -r --recommended, -o --optional

    list commands (possibly output to shell) or NORMAL (download)
    -c --commands 

    package <name>  REQUIRED
    -p --package


main function
 
output specific order of installation 
check if ftp is only link - if yes download
check if package is already downloaded
check if package argument not exist

'''
#if not os.path.exists('dependencies.json'):
 #   print(errors[0])
  #  exit


    


def parserFunction(data):
    parser = argparse.ArgumentParser(description='''This script takes a valid BLFS package as an 
                                                    input and either lists the dependencies,
                                                    or downloads the necessary packages ''')
    parser.add_argument('-l', '--list', help='List dependencies instead of downloading.')
    parser.add_argument('-c', '--commands', help='List installation commands for a given package.')
    parser.add_argument('-r', '--recommended', help='Allow installation of recommended packages.')
    parser.add_argument('-o', '--optional', help='Allow installation of optional packages.')
    parser.add_argument('-p', '--package', help='A BLFS package taken from the book', required=True, type=str)
    args = parser.parse_args()
    if args.package in data:
        print(data[args.package])


with open('dependencies.json', 'r+') as scheme:
    data = json.load(scheme)

parserFunction(data)









