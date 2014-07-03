#!/usr/bin/python

from npm2deb import templates
import codecs
import os

# python 3 import
try:
    from commands import getstatusoutput
except ImportError:
    from subprocess import getstatusoutput

DEBUG_LEVEL = 0


def debug(level, msg):
    if level <= DEBUG_LEVEL:
        print(" debug [%s] - %s" % (level, msg))


def get_npm_version(module_name):
    return getstatusoutput(
        'npm view "%s" version' % module_name)[1].split('\n')[-2].strip()


def get_template(filename):
    result = None
    if filename == 'control':
        result = templates.CONTROL
    elif filename == 'copyright':
        result = templates.COPYRIGHT
    elif filename == 'rules':
        result = templates.RULES
    elif filename == 'wnpp':
        result = templates.WNPP
    elif filename == 'tests/control':
        result = templates.TESTS['control']
    elif filename == 'tests/require':
        result = templates.TESTS['require']
    return result


def get_watch(which):
    if which == 'github':
        return templates.WATCH['github']
    elif which == 'bitbucket':
        return templates.WATCH['bitbucket']
    else:
        return templates.WATCH['fakeupstream']


def get_license(license):
    result = None
    name = license.lower().replace('-', '')
    if name.startswith('gpl2'):
        result = templates.LICENSES['GPL-2']
    elif name.startswith('gpl3'):
        result = templates.LICENSES['GPL-3']
    elif name.startswith('lgpl2'):
        result = templates.LICENSES['LGPL-2']
    elif name.startswith('lgpl3'):
        result = templates.LICENSES['LGPL-3']
    elif name.startswith('mit'):
        result = templates.LICENSES['MIT']
    elif name.startswith('expat'):
        result = templates.LICENSES['Expat']
    elif name.startswith('bsd'):
        result = templates.LICENSES['BSD']
    elif name.startswith('artistic'):
        result = templates.LICENSES['Artistic']
    elif name.startswith('apache'):
        result = templates.LICENSES['Apache']
    else:
        result = 'FIX_ME please specify a license description'
    return result


def change_dir(dir):
    debug(2, "moving to directory %s" % dir)
    try:
        os.chdir(dir)
    except OSError as oserror:
        raise OSError("OSError [%d]: %s at %s" %
                      (oserror.errno, oserror.strerror, oserror.filename))


def create_debian_file(filename, content):
    create_file("debian/%s" % filename, content)


def create_file(filename, content):
    debug(2, "creating file %s" % filename)
    content = u'%s' % content
    if len(content) > 0 and content[-1] != '\n':
        content += '\n'
    with codecs.open(filename, 'w', 'utf-8') as writer:
        writer.write(content)


def create_dir(dir):
    debug(2, "creating directory %s" % dir)
    try:
        os.mkdir(dir)
    except OSError as oserror:
        raise OSError("Error: directory %s already exists." %
                      oserror.filename)
