# BLFS-automation
A simple python script to ease your BLFS project in many ways...


## About this project
BeyondLinuxFromScratch (BLFS) may be a fun project, but with all of the dependencies, some packages are a pain in the neck to install. 
An all-in-one script that will list package dependencies, download them, list the package installation commands, and build the package
     


## Download and installation
To get a local copy up and running follow these simple steps.

### Prerequisites 
<ul>
    <li>A working LFS system (check them out at https://www.linuxfromscratch.org/)</li>
    <li>A working Python environment</li>
    <li>Python package manager (Pip)</li>
    <li>Git (https://www.linuxfromscratch.org/blfs/view/svn/general/git.html)</li>
</ul>

### Installation
1. Clone this repository:
```sh
https://github.com/mas-the-spaz/python-blfs.git
```

2. Install the requirements:
```sh
sudo pip install -r requirements.txt
```
Note: When installing the requirements, this must be done as root - otherwise the wget module

## usage
It is recommended that the main script (deps.py) should always be run as root, in order to prevent errors when installing packages to the system.

First build the latest BLFS package database by running ```python bootstrap.py```.
This 
 


Main usage: deps.py [-h] [-a] [-b PACKAGE] [-c PACKAGE] [-d PACKAGE] [-l PACKAGE] [-o] [-r]

A simple script to list, download, and install any valid BLFS package along with any dependencies.
(Input is cAsE sEnsItIvE)

optional arguments:
  -h, --help            show this help message and exit
  -a, --all             Downloads ALL BLFS packages - uses a lot of time and space
  -b PACKAGE, --build PACKAGE
                        Install a given Package on the system
  -c PACKAGE, --commands PACKAGE
                        List installation (without installing) commands for a given package.      
  -d PACKAGE, --download PACKAGE
                        Downloads a given BLFS package along with all of its dependencies
  -l PACKAGE, --list PACKAGE
                        Lists all of the dependencies for a given BLFS package in order of        
                        installation
  -o, --optional        Also list/download optional packages.
  -r, --recommended     Also list/download recommended packages



## errors?
everything should be run as root!!!!
if requirements.txt is run as normal user, the wget module not work!!!!!


license
