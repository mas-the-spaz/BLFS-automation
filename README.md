# BLFS-automation:
A simple python script to ease your BLFS project in many ways...


## About this project:
This project is designed for people who have built their own LinuxFromScratch (LFS) system, and are now working on the next stage - BeyondLinuxFromScratch (BLFS).
BLFS packages often require many other dependencies to work, and sometimes it is a bit cumbersome to install all of those.
    
<br><br>
This project contains two scripts: The first, ```bootstrap.py``` will build a local database containing all the dependencies, the urls, and the installation commands.

The second script ```deps.py```, will parse through the database, and depending on the options, will either list the dependencies, download all the dependencies, download **all** packages (uses a lot of time and space), list installation commands ofr a given package, or install the given package on the BLFS system.

     


## Download and installation:
To get a local copy up and running follow these steps.

### Prerequisites:
<ul>
    <li>A working LFS system (check them out at https://www.linuxfromscratch.org/)</li>
    <li>A working Python environment</li>
    <li>Python package manager (Pip)</li>
    <li>Git (https://www.linuxfromscratch.org/blfs/view/svn/general/git.html)</li>
</ul>

### Installation:
1. Clone this repository:
```
git clone https://github.com/mas-the-spaz/python-blfs.git
```

2. Install the requirements:
```
sudo pip install -r requirements.txt
```
Note: Installing the requirements, must be done as root - this fixes a bug where the ```wget``` module does not get imported.

## Usage:
It is recommended that the main script (deps.py) should always be run as root, in order to prevent errors when installing packages to the system.

First build the latest BLFS package database by running ```# python bootstrap.py```.
This will ensure that you have a database with the latest BLFS version.

Alternatively, you can just use the included dependencies.json file. At the time of writing, the version is BLFS 10.1.

 
The main script ```deps.py```, has many options to list, download, list commands, or install a package.
Note: once again it is *highly* recommended that you run this as ```root```!

Main usage: ```python deps.py [-h] [-a] [-b PACKAGE] [-c PACKAGE] [-d PACKAGE] [-l PACKAGE] [-o] [-r]```

```
optional arguments:
  -a, --all             Downloads ALL BLFS packages - uses a lot of time and space


  -b PACKAGE, --build PACKAGE
                        Install a given Package on the system

  -c PACKAGE, --commands PACKAGE
                        List installation (without installing) commands for a given package. 


  -d PACKAGE, --download PACKAGE
                        Downloads a given BLFS package along with all of its dependencies


  -l PACKAGE, --list PACKAGE
                        Lists all of the dependencies for a given BLFS package in order of installation


  -o, --optional        Also list/download optional packages.


  -r, --recommended     Also list/download recommended packages
  ```

## Todo:
<ul>
<li>Add MD5 hash check and verification</li>
<li>Fix SSL problems (is there a way to do local certificate stuff?)</li>
</ul>




