import argparse
import json
import os
import wget

''''
Todo:
1) rewrite 'all' function
2) consolidate code
4) map, filter, reduce
5) basic autocomplete checker (maybe just version number)
6) check if package is already downloaded
7) install packages in this order
'''

default_download_path = '/blfs_sources/'
# change above line for the default download location for the packages

messages = ["Dependencies.json not found! Try running bootstrap.py to rebuild dependency database",
            "no dependencies found for ", "Download directory not found - creating one.",
            "Creation of download directory failed!", "Successfully created directory.",
            "Found existing download directory. Proceeding...", "Install packages in this order:"]

extensions = ['.bz2', '.tar.xz', '.zip', '.tar.gz', '.patch', '.tgz']


def CheckDir():
    if not os.path.exists(default_download_path):
        print(messages[2])
        try:
            os.mkdir(default_download_path, 0o755)
        except OSError:
            print(messages[3])
            exit(1)
        else:
            print(messages[4])
    else:
        print(messages[5])
    return


def FtpUrlCheck(UrlsList):
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
    commands = []
    if not pkg in dat:
        print('{0} "{1}"'.format(messages[1], pkg))
        exit()
    for command in dat[pkg]['Commands']:  # list commands
        commands.append(command)
    return commands


def BuildPkg(dat, pkg):
    CheckDir()
    # check if package is downloaded (default dl dir is /blfs_sources/)
    # if data[dep][url] strip last backslash exists
    # if not download it
    # untar package (diff for zip/bz2/gz/xz)
    # get installation commands from json file
    # for each command, pipe into bash
    commands = ListCommands(dat, pkg)
    for command in commands:
        print(command)


def DownloadAll(dat, exts=None):  # list (eventually download) all packages
    CheckDir()
    for PackageData in dat:  # package
        NonFtp = FtpUrlCheck(dat[PackageData]['url'])
        for url in NonFtp:  # url list
            for i in exts:  # consolidate for loops
                if i in url:
                    wget.download(url, default_download_path)
                    print(url)


def DownloadDeps(dat, pkg, exts, rec=None, opt=None):
    CheckDir()
    DlList = DepsList(dat, pkg, rec, opt)
    for package in DlList:
        NonFtp = FtpUrlCheck(dat[package]['url'])
        for url in NonFtp:  # url list
            for i in exts:  # consolidate for loops
                if i in url:
                    if not os.path.exists(os.path.basename(url)):
                        wget.download(url, default_download_path + os.path.basename(url))
                        print('Downloading: {0}\n'.format(url))


def DepsList(dat, pkg, rec=None, opt=None):
    if not pkg in dat:
        print('{0} "{1}"'.format(messages[1], pkg))
        exit()
    else:
        __types = ['required']
    if rec:
        __types.append('recommended')
    elif opt:  # if both flags (-o, -r) are passed, warn user that defaults to rec only
        __types.extend(['recommended', 'optional'])
    return GetChild(dat, [pkg], __types)


def GetChild(dat, PkgList, types):  # way to many for loops!!!!
    # Gets the child dependency of each package and recursively lists until the end of the tree
    for pkg in PkgList:
        if pkg in dat:
            for index in types:
                for dep in dat[pkg]['Dependencies'][index]:
                    if not dep in PkgList:  # prevents circular dependency problems
                        PkgList.append(dep)
    return PkgList


def Output(lst, reverse):  # takes list and outputs to stdout
    if reverse:
        lst.reverse()
    else:
        pass
    for thing in lst:
        print(thing)


def parserFunction(dat):
    parser = argparse.ArgumentParser(description='This script takes a valid BLFS package as an input and either lists '
                                                 'the dependencies, or downloads the necessary packages. (Input is '
                                                 'cAsE sEnsItIvE)',
                                     prog='deps.py')
    parser.add_argument('-a', '--all', help='Will download ALL packages. Uses a lot of time and '
                                            'space', action='store_true')
    parser.add_argument('-b', '--build', help='Install a given Package', metavar='PACKAGE', default=False)
    parser.add_argument('-c', '--commands', metavar='PACKAGE', help='List installation (without installing) commands '
                                                                    'for a given package.', default=False)
    parser.add_argument('-d', '--download', help='Download given BLFS package', metavar='PACKAGE')
    parser.add_argument('-l', '--list', metavar='PACKAGE', help='List dependencies instead of downloading.',
                        default=False)
    parser.add_argument('-o', '--optional', help='Allow installation of optional packages.', action='store_true')
    parser.add_argument('-r', '--recommended', help='Allow installation of recommended packages.',
                        default=False, action='store_true')
    args = parser.parse_args()

    if args.download:
        DownloadDeps(dat, args.download, extensions, args.recommended, args.optional)
    elif args.list:
        print(messages[6])
        Output(DepsList(dat, args.list, args.recommended, args.optional), True)
    elif args.commands:
        Output(ListCommands(dat, args.commands), False)
    elif args.all:
        DownloadAll(dat, extensions)
    elif args.build:
        BuildPkg(dat, args.build)
    else:
        parser.print_help()


if not os.path.exists('dependencies.json'):
    print(messages[0])
    exit()

with open('dependencies.json', 'r+') as scheme:
    data = json.load(scheme)

parserFunction(data)
