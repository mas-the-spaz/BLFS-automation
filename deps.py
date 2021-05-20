#!/usr/bin/python3

import wget
import argparse
import json
import os
import tarfile
import zipfile
import subprocess

default_download_path = '/blfs_sources/'
# change above line for the default download location for the packages

messages = ["Dependencies.json not found! Try running 'bootstrap.py' to rebuild the dependency database",
            "no dependencies found for ", "Download directory not found - creating one.",
            "Creation of download directory failed!", "Successfully created directory.",
            "Found existing download directory. Proceeding...", "Install packages in this order:",
            "Downloaded file could not be decompressed!",
            "A simple script to list, download, and install any valid BLFS package along with any dependencies. "
            "(Input is cAsE sEnsItIvE)",
            "Downloads ALL BLFS packages - uses a lot of time and space", "Install a given Package on the system",
            "List installation (without installing) commands for a given package.",
            "Downloads a given BLFS package along with all of its dependencies",
            "Lists all of the dependencies for a given BLFS package in order of installation",
            "Also list/download optional packages.",
            "Also list/download recommended packages"]

extensions = ['.bz2', '.tar.xz', '.zip', '.tar.gz', '.patch', '.tgz']


def CheckDir():  # download directory housekeeping function
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
    os.chdir(default_download_path)
    return


def FtpUrlFilter(UrlsList):  # removes ftp links from url list, but only if they ar duplicates
    NewList = []
    i = 0
    while i < len(UrlsList):
        if (i % 2) == 0:
            NewList.append(UrlsList[i])
        elif not 'ftp://' in UrlsList[i]:
            NewList.append(UrlsList[i])
        i += 1
    return NewList


def ListCommands(dat, pkg):  # list the installation commands for a given BLFS package
    CommandsList = []
    if not pkg in dat:
        print('{0} "{1}"'.format(messages[1], pkg))
        exit()
    for command in dat[pkg]['Commands']:
        CommandsList.append(command)
    return CommandsList


def BuildPkg(dat, pkg):  # install a given BLFS package on the system
    DownloadDeps(dat, [pkg], extensions)
    FileToExtract = dat[pkg]['url'][0]
    if tarfile.is_tarfile(os.path.basename(FileToExtract)):
        with tarfile.open(os.path.basename(FileToExtract), 'r') as tar_ref:
            tar_ref.extractall()
            os.chdir(tar_ref.getnames()[0])

    if zipfile.is_zipfile(os.path.basename(FileToExtract)):
        with zipfile.ZipFile(os.path.basename(FileToExtract), 'r') as zip_ref:
            print(os.path.splitext(os.path.basename(FileToExtract))[0])
            zip_ref.extractall(os.path.splitext(os.path.basename(FileToExtract))[0])
            os.chdir(os.path.splitext(os.path.basename(FileToExtract))[0])

    commands = ListCommands(dat, pkg)
    for command in commands:
        install = input('Should I run "{}"? <y/n>\n'.format(command))
        if install.lower() == 'y':
            print('running {}'.format(command))
            subprocess.call(['/bin/sh', '-c', command])  # output command to shell
        else:
            pass


def DownloadDeps(dat, dlList, exts):  # download all urls in dlList (can be all urls or just some dependencies)
    CheckDir()
    for package in dlList:
        if package in dat:
            for url in FtpUrlFilter(dat[package]['url']):
                for i in exts:
                    if i in url:
                        if not os.path.isfile(os.path.basename(url)):
                            print('\nDownloading: {0}\n'.format(url))
                            wget.download(url, os.path.basename(url))
                        else:
                            print('{} already has been downloaded'.format(os.path.basename(url)))


def ListDeps(dat, pkg, rec=None, opt=None):  # lists all dependencies (can be required, recommended, and/or optional)
    __types = []
    if not pkg in dat:
        print('{0} "{1}"'.format(messages[1], pkg))
        exit()
    else:
        __types.append('required')
    if rec:
        __types.append('recommended')
    elif opt:
        __types.extend(['recommended', 'optional'])
    return GetChild(dat, [pkg], __types)


def GetChild(dat, PkgList, types):  # recursively lists all dependencies for a given package
    for pkg in PkgList:
        if pkg in dat:
            for index in types:
                for dep in dat[pkg]['Dependencies'][index]:
                    if not dep in PkgList:  # prevents circular dependency problems
                        PkgList.append(dep)
    return PkgList


def Output(lst, reverse):  # output function
    if reverse:
        print(messages[6])
        lst.reverse()
    else:
        pass
    for thing in lst:
        print(thing)


def ParserFunction(dat):  # main parser function
    parser = argparse.ArgumentParser(description=messages[8], prog='deps.py')
    parser.add_argument('-a', '--all', help=messages[9], action='store_true')
    parser.add_argument('-b', '--build', help=messages[10], metavar='PACKAGE', default=False)
    parser.add_argument('-c', '--commands', metavar='PACKAGE', help=messages[11], default=False)
    parser.add_argument('-d', '--download', help=messages[12], metavar='PACKAGE')
    parser.add_argument('-l', '--list', metavar='PACKAGE', help=messages[13], default=False)
    parser.add_argument('-o', '--optional', help=messages[14], action='store_true')
    parser.add_argument('-r', '--recommended', help=messages[15], action='store_true')
    args = parser.parse_args()

    if args.download:
        DownloadDeps(dat, ListDeps(dat, args.download, args.recommended, args.optional), extensions)
    elif args.list:
        Output(ListDeps(dat, args.list, args.recommended, args.optional), True)
    elif args.commands:
        Output(ListCommands(dat, args.commands), False)
    elif args.all:
        DownloadDeps(dat, dat, extensions)
    elif args.build:
        BuildPkg(dat, args.build)
    else:
        parser.print_help()


if not os.path.exists('dependencies.json'):
    print(messages[0])
    exit()

with open('dependencies.json', 'r') as scheme:
    data = json.load(scheme)

ParserFunction(data)
