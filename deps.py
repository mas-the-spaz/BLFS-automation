import argparse
import json
import os
from itertools import product
import wget

''''
Todo:
1) rewrite 'all' function
2) consolidate code

'''

errors = ["Dependencies.json not found! Try running bootstrap.py to rebuild dependency database",
          "no dependencies found for "]

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


def FtpUrlCheck(UrlsList):  # removes second http also....
    NewList = []
    i = 0
    while i < len(UrlsList):
        if (i % 2) == 0:
            NewList.append(UrlsList[i])
        elif not 'ftp://' in UrlsList[i]:
            print(UrlsList[i])
            NewList.append(UrlsList[i])
        i += 1

    return NewList


def ListCommands(dat, pkg):
    if not pkg in dat:
        print('{0} "{1}"'.format(errors[1], pkg))
        exit()
    for command in dat[pkg]['Commands']:  # list commands
        print(command)


def DownloadAll(dat, exts=None):  # list (eventually download) all packages
    for PackageData in dat:  # package
        NonFtp = FtpUrlCheck(dat[PackageData]['url'])
        for url in NonFtp:  # url list
            for i in exts:
                if i in url:
                    # create download directory and wget
                    print(url)


def DownloadDeps(dat, pkg, rec=None, opt=None):  # maybe use *args for dl types?
    # calls DepsList than download from the list?
    if opt:
        print('required, recommended, and optional')
    if rec:
        print('required and recommended')

    print(dat[pkg])


def DepsList(dat, pkg, rec=None, opt=None):
    if not pkg in dat:
        print('{0} "{1}"'.format(errors[1], pkg))
        exit()
    # list deps based on flags provided (opt > rec > req)
    temp = []
    deps = []
    for dep in dat[pkg]['Dependencies']['optional']:
        print(dep)



def parserFunction(dat):
    parser = argparse.ArgumentParser(description='This script takes a valid BLFS package as an input and either lists '
                                                 'the dependencies, or downloads the necessary packages ',
                                     prog='deps.py')
    parser.add_argument('-a', '--all', help='Will download ALL packages. Uses a lot of time and '
                                            'space', action='store_true')
    parser.add_argument('-c', '--commands', metavar='PACKAGE', help='List installation commands for a given package.',
                        default=False)
    parser.add_argument('-d', '--download', help='Download given BLFS package', metavar='PACKAGE')
    parser.add_argument('-l', '--list', metavar='PACKAGE', help='List dependencies instead of downloading.',
                        default=False)
    parser.add_argument('-o', '--optional', help='Allow installation of optional packages.', action='store_true')
    parser.add_argument('-r', '--recommended', help='Allow installation of recommended packages.',
                        default=False, action='store_true')
    args = parser.parse_args()

    if args.download:
        DownloadDeps(dat, args.download, args.recommended, args.optional)
    elif args.list:
        DepsList(dat, args.list, args.recommended, args.optional)
    elif args.commands:
        ListCommands(dat, args.commands)  # maybe add basic autocomplete
    elif args.all:
        DownloadAll(dat, extensions)
    else:
        parser.print_help()


if not os.path.exists('dependencies.json'):
    print(errors[0])
    exit()

with open('dependencies.json', 'r+') as scheme:
    data = json.load(scheme)

parserFunction(data)
