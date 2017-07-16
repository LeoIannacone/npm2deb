npm2deb
=======

A script to make faster and easier packaging nodejs modules

## Requirements
You need to install the following dependencies on your system:
```
sudo apt-get install devscripts npm python3-dateutil node-github-url-from-git
```
Please make sure that the environment variables  **DEBEMAIL** (or **EMAIL**) and **DEBFULLNAME** are defined  correctly.

## Install
```
sudo python3 setup.py install
```

## Usage
Simply take a look at help option:
```
$ npm2deb -h

usage: npm2deb [-h] [-D DEBUG] [-v]
               {create,view,depends,rdepends,search,itp,license} ...

optional arguments:
  -h, --help            show this help message and exit
  -D DEBUG, --debug DEBUG
                        set debug level
  -v, --version         show program's version number and exit

commands:
  {create,view,depends,rdepends,search,itp,license}
    create              create the debian files
    view                a summary view of a node module
    depends             show module dependencies in npm and debian
    rdepends            show the reverse dependencies for module
    search              look for module in debian project
    itp                 print a itp bug template
    license             print license template and exit

```

### Example
A workflow example is shown here: [wiki.debian.org/Javascript/Nodejs/Npm2Deb](https://wiki.debian.org/Javascript/Nodejs/Npm2Deb)

In most cases a simple command like the following is enough:
```
$ npm2deb create node-module
```
