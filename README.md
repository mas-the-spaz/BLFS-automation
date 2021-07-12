# BLFS-automation:
A simple python script to ease your BLFS project in many ways...


## About this project:
This project is designed for people who have built their own LinuxFromScratch (LFS) system, and are now working on the next stage - BeyondLinuxFromScratch (BLFS).
BLFS packages often require many other dependencies to work, and sometimes it is a bit cumbersome to install all of those.
    
<br><br>
This project contains two scripts: The first, ```bootstrap.py``` will build a local database containing all the dependencies, the urls, and the installation commands.

The second script, ```deps.py```, will parse through the database, and depending on the options, either list the dependencies, download all the dependencies, download **all** packages (uses a lot of time and space), list installation commands for a given package, or install the given package on the BLFS system.

     


## Download and installation:
To get a local copy up and running follow these steps.

### Prerequisites:
<ul>
    <li>A working LFS system (check them out at https://www.linuxfromscratch.org/)</li>
    <li>A working internet connection - you may need to install a couple of BLFS packages like NetworkManager, DHCPClient, and WPA-supplicant.</li>
    <li>A working Python environment</li>
    <li>Python3 package manager (Pip)</li>
    <li>Git (https://www.linuxfromscratch.org/blfs/view/svn/general/git.html)</li>
</ul>

### Installation:
1. Clone this repository:
```
git clone https://github.com/ahron-maslin/BLFS-automation.git 
```

2. Install the requirements:
```
sudo pip install -r requirements.txt
```
Note: Installing the requirements, must be done as root - this fixes a bug where the ```wget``` module does not get imported.

## Usage:
It is recommended that the main script ```deps.py``` should always be run as root, in order to prevent errors when installing packages to the system.

First build the latest BLFS package database by running ```# python3 bootstrap.py```.
This will ensure that you have a database with the latest BLFS version.

Alternatively, you can just use the included ```dependencies.json``` file. At the time of writing, the version is BLFS 10.1.

 
The main script ```deps.py```, has many options to list, download, list commands, or install a package.
Note: once again it is *highly* recommended that you always run this as ```root```!

Main usage: ```python deps.py [-h] [-a] [-b PACKAGE] [-c PACKAGE] [-d PACKAGE] [-l PACKAGE] [-o] [-r]```

Note: It is recommended to follow along the installation process in the BLFS book. This tool is not perfect and I have not tested every BLFS package. There are still some issues with circular dependencies, and at the moment it is best to moniter everything to prevent problems. Additionally, the ```-b (build)``` option will prompt the user to run EVERY command provided for the specific package. Some commands can only be run if optional dependencies are installed (like Texlive, Docbook, etc.). Furthermore, some packages require further kernel configuration (and recompilation) as a prerequisite for installation.

```
  -h, --help                        show this help message and exit

  -a, --all                         Downloads ALL BLFS packages - uses a lot of time and space.

  -b PACKAGE, --build PACKAGE       Install a given Package on the system.

  -c PACKAGE, --commands PACKAGE    List installation (without installing) commands for a given package.
  
  -d PACKAGE, --download PACKAGE    Downloads a given BLFS package along with all of its dependencies.

  -e PACKAGE, --everything PACKAGE  Downloads and installs the given package with all of it's dependencies.

  -l PACKAGE, --list PACKAGE        Lists all of the dependencies for a given BLFS package in order of installation.

  -o, --optional                    Also list/download optional packages.

  -r, --recommended                 Also list/download recommended packages.

  -s PACKAGE, --search PACKAGE      Search for a given package.
  ```

## Additional options:
If you are building BLFS with Systemd, you must uncomment a line in the ```bootstrap.py``` file to get the right sources. Run the following command to fix that:
```
sed -i '/stable-systemd/s/^# *//' bootstrap.py
```

If you would like to change the default download location, you can modify it in ```deps.py```.


## Contributers: 
Ahron Maslin (creator, maintainer, and designer), Josh W. (moral support), Dan the Man (Chief Psychologist)




