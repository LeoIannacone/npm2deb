npm2deb
=======

a script to make faster and easier packaging nodejs modules

## Requirements
You need **npm** installed on your system:
```
sudo apt-get install nmp
```
Please, take care to have defined **DEBEMAIL** (or **EMAIL** and **DEBFULLNAME**) environment variables correctly.

## Install
```
sudo python setup.py install
```

## Usage
Simply take a look at help option:
```
$ npm2deb -h

usage: npm2deb [options] node_module | -p [license]

positional arguments:
  node_module           node module available via npm

optional arguments:
  -h, --help            show this help message and exit
  -d DEBHELPER, --debhelper DEBHELPER
                        specify debhelper version [default: 9]
  -l LICENSE, --license LICENSE
                        license used for debian files [default: GPL-3]
  -n, --noclean         do not remove files downloaded with npm
  -p [PRINTLICENSE], --printlicense [PRINTLICENSE]
                        print license template and exit
  -s STANDARDS, --standards STANDARDS
                        set standards-version [default: 3.9.5]
  -D DEBUG, --debug DEBUG
                        set debug level
```

### Example
In the most of cases a simple command like this is enough:
```
$ npm2deb bytes
```
