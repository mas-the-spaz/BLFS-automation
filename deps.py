import argparse
import json
import os

errors = ["Dependencies.json not found! Try running bootstrap.py to rebuild dependency database",
          "no dependencies found for (package arguments)"]

extensions = ['.bz2', '.tar.xz', '.zip', '.tar.gz', '.patch', '.tgz']

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

if -d package -- download function          ---opt ---override everything
if -l package -- list function              ---opt 
if -r or -o -- also do those deps           ---opt ---only works with -l or -d CHECK THAT   
if -a download all ONLY                     ---opt 
if -c list commands for that package        ---opt


'''

'''
JSON scheme
{
'Package Name': {                                         
        'Version': '1.0.0',                               
        'URL': ['http://asdfasdfasdf','http://patch],     
        'Deps': {                                         
            'Required': ['first', 'second'],              
            'Recommended': ['first', 'second'],           
            'Optional': ['first', 'second']               
            }, 
        'Commands': ['Installation commands']             
        }
}
'''


def ListCommands(dat, arguments):
    for command in dat[arguments.commands]['Commands']:  # ---list commands
        print(command)


def DownloadAll(dat):
    for package in dat:
        for url in dat[package]['url']:
            for i in extensions:
                if i in url:
                    print(url)


def DownloadDeps(dat, args):
    if args.optional:
        print('hi kupfer')


def DepsList(dat, args):
    print('hi kupfer')


def parserFunction(dat):
    parser = argparse.ArgumentParser(description='This script takes a valid BLFS package as an input and either lists '
                                                 'the dependencies, or downloads the necessary packages ', prog='deps')
    parser.add_argument('-a', '--all', help='Will download ALL packages. Uses a lot of time and '
                                            'space', action='store_true')
    parser.add_argument('-c', '--commands', metavar='PACKAGE', help='List installation commands for a given package.',
                        default=False)
    parser.add_argument('-d', '--download', help='Download given BLFS package', metavar='PACKAGE')
    parser.add_argument('-l', '--list', metavar='PACKAGE', help='List dependencies instead of downloading.',
                        default=False)
    parser.add_argument('-o', '--optional', help='Allow installation of optional packages.', default=False,
                        action='store_true')
    parser.add_argument('-r', '--recommended', help='Allow installation of recommended packages.',
                        default=False, action='store_true')
    args = parser.parse_args()
    if not any(vars(args).values()):
        parser.print_help()

    if args.download or args.commands or args.list in dat:
        if args.download:
            DownloadDeps(dat, args)
        elif args.commands:
            ListCommands(dat, args)
        elif args.list:
            DepsList(dat, args)

    if args.all:
        DownloadAll(dat)


if not os.path.exists('dependencies.json'):
    print(errors[0])
    exit()

with open('dependencies.json', 'r+') as scheme:
    data = json.load(scheme)

parserFunction(data)
