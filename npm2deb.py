#!/usr/bin/python

from optparse import OptionParser
from npm2deb import Npm2Deb
from npm2deb import utils
import os

def main():
  usage = 'usage %prog [options] package_name'
  parser = OptionParser(usage)
  parser.add_option('-d', '--debug', help='set debug level')
  opts, args = parser.parse_args()

  if len(args) is not 1:
    parser.error('Please specify a package_name.')
    exit(1)

  if opts.debug:
    try:
      utils.DEBUG_LEVEL = int(opts.debug)
    except ValueError:
      print("Error: debug level must be an integer.")
      exit(1)

  package_name = args[0]
  savedPath = os.getcwd()
  utils.create_dir(package_name)
  utils.change_dir(package_name)

  npm2deb = Npm2Deb(package_name)
  npm2deb.start()

  utils.change_dir(savedPath)

  print("""
This is not a crystal ball, so please take a look at auto-generated files.
This command could help:
$ grep -r FIX_ME %s/%s/debian/*
You can use uscan after fixing watch file and start to work on packaging.
""" % (package_name, npm2deb.debian_name))


if __name__ == '__main__':
    main()