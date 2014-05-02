npm2deb
=======

a script to make faster and easier packaging nodejs modules

## Requirements
You need **npm** installed on your system:
```
sudo apt-get install npm
```
Please, take care to have defined **DEBEMAIL** (or **EMAIL**) and **DEBFULLNAME** environment variables correctly.

## Install
```
sudo python setup.py install
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
In the most of cases a simple command like this is enough:
```
$ npm2deb create bytes
```
