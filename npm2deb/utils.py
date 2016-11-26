from subprocess import getstatusoutput as _getstatusoutput
import codecs as _codecs
import os as _os

from npm2deb import templates as _templates


DEBUG_LEVEL = 0


def debug(level, msg):
    if level <= DEBUG_LEVEL:
        print(" debug [%s] - %s" % (level, msg))


def get_npm_version(module_name):
    return _getstatusoutput(
        'npm view "%s" version' % module_name)[1].split('\n')[-2].strip()


def get_template(filename):
    result = None
    if filename == 'control':
        result = _templates.CONTROL
    elif filename == 'copyright':
        result = _templates.COPYRIGHT
    elif filename == 'rules':
        result = _templates.RULES
    elif filename == 'wnpp':
        result = _templates.WNPP
    elif filename == 'tests/control':
        result = _templates.TESTS['control']
    elif filename == 'tests/require':
        result = _templates.TESTS['require']
    return result


def get_watch(which):
    if which == 'github':
        return _templates.WATCH['github']
    elif which == 'bitbucket':
        return _templates.WATCH['bitbucket']
    else:
        return _templates.WATCH['fakeupstream']


def get_license(license):
    result = None
    name = license.lower().replace('-', '')
    if name.startswith('gpl2'):
        result = _templates.LICENSES['GPL-2']
    elif name.startswith('gpl3'):
        result = _templates.LICENSES['GPL-3']
    elif name.startswith('lgpl2'):
        result = _templates.LICENSES['LGPL-2']
    elif name.startswith('lgpl3'):
        result = _templates.LICENSES['LGPL-3']
    elif name.startswith('mit'):
        result = _templates.LICENSES['MIT']
    elif name.startswith('expat'):
        result = _templates.LICENSES['Expat']
    elif name.startswith('bsd4'):
        result = _templates.LICENSES['BSD-4-clause']
    elif name.startswith('bsd2'):
        result = _templates.LICENSES['BSD-2-clause']
    elif name.startswith('bsd'):
        result = _templates.LICENSES['BSD-3-clause']
    elif name.startswith('artistic'):
        result = _templates.LICENSES['Artistic']
    elif name.startswith('apache'):
        result = _templates.LICENSES['Apache']
    elif name.startswith('isc'):
        result = _templates.LICENSES['ISC']
    else:
        result = 'FIX_ME specify a license, see: ' \
                 'https://www.debian.org/doc/packaging-manuals/' \
                 'copyright-format/1.0/#license-specification'
    return result


def change_dir(dir):
    debug(2, "moving to directory %s" % dir)
    try:
        _os.chdir(dir)
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
    with _codecs.open(filename, 'w', 'utf-8') as writer:
        writer.write(content)


def create_dir(dir):
    debug(2, "creating directory %s" % dir)
    try:
        _os.mkdir(dir)
    except OSError as oserror:
        raise OSError("Error: directory %s already exists." %
                      oserror.filename)

def debianize_name(name):
    return name.replace('_', '-').lower()

def get_npmjs_homepage(name):
    return 'https://npmjs.com/package/' + name
