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

if package only -- download function        ---pos
if -l package -- list function              ---opt (default is download)
if -r or -o -- also do those deps           ---opt (default is only required)
if -a download all ONLY
if -c list commands for that package


'''

'''
JSON scheme
{
'Package Name': {                                         ---string
        'Version': '1.0.0',                               ---string
        'URL': ['http://asdfasdfasdf','http://patch],     ---array (includes patches urls)
        'Deps': {                                         ---dict or None
            'Required': ['first', 'second'],              ---array or None
            'Recommended': ['first', 'second'],           ---array or None
            'Optional': ['first', 'second']               ---array or None
            }, 
        'Commands': ['Installation commands']             ---array
        }
}
'''


def ListCommands(dat, arguments):
    for command in dat[arguments.commands]['Commands']:  # ---list commands
        print(command)


def DownloadAll(dat):
    for package in dat:
        for url in dat[package]['url']:
            print(url)


def parserFunction(dat):
    parser = argparse.ArgumentParser(description='This script takes a valid BLFS package as an input and either lists '
                                                 'the dependencies, or downloads the necessary packages ', prog='deps')
    parser.add_argument('-a', '--all', help='Will download ALL packages. Uses a lot of time and '
                                            'space', action='store_true')
    parser.add_argument('-c', '--commands', metavar='PACKAGE', help='List installation commands for a given package.',
                        default=False)
    parser.add_argument('-l', '--list', metavar='PACKAGE', help='List dependencies instead of downloading.',
                        default=False)
    parser.add_argument('-o', '--optional', metavar='', help='Allow installation of optional packages.', default=False)
    parser.add_argument('-r', '--recommended', metavar='', help='Allow installation of recommended packages.',
                        default=False)
    parser.add_argument('-d', '--download', help='Download given BLFS package', metavar='PACKAGE')
    args = parser.parse_args()
    # if no args print help

    if args.download in dat:
        # case break
        if args.commands:
            ListCommands(dat, args)

    if args.all:
        DownloadAll(dat)


if not os.path.exists('dependencies.json'):
    print(errors[0])
    exit()

with open('dependencies.json', 'r+') as scheme:
    data = json.load(scheme)

parserFunction(data)
