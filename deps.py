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

if package only -- download function
if -l package -- list function
if -c or -o -- also do those deps


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
if not os.path.exists('dependencies.json'):
    print(errors[0])
    exit()


def parserFunction(dat):
    parser = argparse.ArgumentParser(description='This script takes a valid BLFS package as an input and either lists '
                                                 'the dependencies, or downloads the necessary packages ', prog='deps')
    parser.add_argument('-l', '--list', metavar='PACKAGE', help='List dependencies instead of downloading.')  # optional
    parser.add_argument('-a', '--all', metavar='', help='Will download or list ALL packages. Uses a lot of time and '
                                                        'space')  # optional
    parser.add_argument('-c', '--commands', metavar='PACKAGE', help='List installation commands for a given package.')  # optional
    parser.add_argument('-r', '--recommended', metavar='', help='Allow installation of recommended packages.')  # optional
    parser.add_argument('-o', '--optional', metavar='', help='Allow installation of optional packages.')  # optional
    parser.add_argument('package', help='A BLFS package taken from the book', type=str)  # pos
    args = parser.parse_args()
    if args.package in dat:
        # print(data[args.package])
        for command in dat[args.package]['Commands']:  # ---list commands
            print(command)


with open('dependencies.json', 'r+') as scheme:
    data = json.load(scheme)

parserFunction(data)
