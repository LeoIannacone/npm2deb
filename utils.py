#!/usr/bin/python

import templates
import os

DEBUG_LEVEL = 3

def debug(level, msg):
  if level <= DEBUG_LEVEL:
    print( " debug [%s] - %s" % (level, msg))

def get_template(filename):
  result = None
  if filename is 'control':
    result = templates.CONTROL
  elif filename is 'copyright':
    result = templates.COPYRIGHT
  elif filename is 'rules':
    result = templates.RULES
  return result

def get_license(license):
  result = None
  name = license.lower().replace('-', '')
  if name.startswith('gpl2'):
    result = templates.LICENSE_GPL_2
  elif name.startswith('gpl3'):
    result = templates.LICENSE_GPL_3
  elif name.startswith('lgpl2'):
    result = templates.LICENSE_LGPL_2
  elif name.startswith('lgpl3'):
    result = templates.LICENSE_GPL_3    
  elif name.startswith('mit'):
    result = templates.LICENSE_MIT
  elif name.startswith('bsd'):
    result = templates.LICENSE_BSD
  elif name.startswith('artistic'):
    result = templates.LICENSE_ARTISTIC
  elif name.startswith('apache'):
    result = templates.LICENSE_APACHE
  else:
    result = 'FIX_ME: please specify a license description'
  return result

def change_dir(dir):
  debug(2, "moving to directory %s" % dir)
  try:
    os.chdir(dir)
  except OSError as e:
    print ("OSError [%d]: %s at %s" % (e.errno, e.strerror, e.filename))
    exit(1)

def create_debian_file(filename, content):
  create_file("debian/%s" % filename, content)

def create_file(filename, content):
  debug(2, "creating file %s", filename)
  with open(filename) as fd:
    fd.write(content)

def create_dir(dir):
  debug(2, "creating directory %s" % dir)
  try:
    os.mkdir(dir)
  except OSError as e:
    print ("Error: directory %s already exists." % (e.filename))
    exit(1)