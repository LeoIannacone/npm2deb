from subprocess import getstatusoutput as _getstatusoutput
from subprocess import Popen as _Popen
from subprocess import PIPE as _PIPE
import codecs as _codecs
import locale as _locale
import os as _os
from pathlib import Path as _Path

from npm2deb import templates as _templates


DEBUG_LEVEL = 0
# files starting with this strings will not be included in debian/install
IGNORED_FILES = [
    '.',                                  # dotfiles
    'readme',                             # readme
    'history', 'changelog',               # history files
    'license', 'copyright', 'licence',    # legal files
    'gruntfile', 'gulpfile', 'makefile',  # buid system files
    'karma.conf', 'bower.json',
    'test'                                # test files
]


def debug(level, msg):
    if level <= DEBUG_LEVEL:
        print(" debug [%s] - %s" % (level, msg))


def get_npm_version(module_name):
    return _getstatusoutput(
        'npm view "%s" version' % module_name)[1].split('\n')[-2].strip()


def is_ignored(filename):
    filename = filename.lower()
    for pattern in IGNORED_FILES:
        if filename.startswith(pattern):
            return True

    return False


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
        path = _Path(dir)
        path.mkdir(parents=True)
    except OSError as oserror:
        raise OSError("Error: directory %s already exists." %
                      oserror.filename)

def parse_name(name):
    parts = name.partition('@')
    return parts[0], parts[2]


def debianize_name(name):
    return name.replace('_', '-').replace('@', '').replace('/', '-').lower()


def get_npmjs_homepage(name):
    return 'https://npmjs.com/package/' + name

# taken from https://github.com/pallets/click/blob/master/click/_unicodefun.py


def verify_python3_env():
    """Ensures that the environment is good for unicode on Python 3."""
    try:
        fs_enc = _codecs.lookup(_locale.getpreferredencoding()).name
    except Exception:
        fs_enc = 'ascii'
    if fs_enc != 'ascii':
        return

    extra = ''
    if _os.name == 'posix':
        rv = _Popen(['locale', '-a'], stdout=_PIPE,
                    stderr=_PIPE).communicate()[0]
        good_locales = set()
        has_c_utf8 = False

        # Make sure we're operating on text here.
        if isinstance(rv, bytes):
            rv = rv.decode('ascii', 'replace')

        for line in rv.splitlines():
            locale = line.strip()
            if locale.lower().endswith(('.utf-8', '.utf8')):
                good_locales.add(locale)
                if locale.lower() in ('c.utf8', 'c.utf-8'):
                    has_c_utf8 = True

        extra += '\n\n'
        if not good_locales:
            extra += (
                'Additional information: on this system no suitable UTF-8\n'
                'locales were discovered.  This most likely requires resolving\n'
                'by reconfiguring the locale system.'
            )
        elif has_c_utf8:
            extra += (
                'This system supports the C.UTF-8 locale which is recommended.\n'
                'You might be able to resolve your issue by exporting the\n'
                'following environment variables:\n\n'
                '    export LC_ALL=C.UTF-8\n'
                '    export LANG=C.UTF-8'
            )
        else:
            extra += (
                'This system lists a couple of UTF-8 supporting locales that\n'
                'you can pick from.  The following suitable locales were\n'
                'discovered: %s'
            ) % ', '.join(sorted(good_locales))

        bad_locale = None
        for locale in _os.environ.get('LC_ALL'), _os.environ.get('LANG'):
            if locale and locale.lower().endswith(('.utf-8', '.utf8')):
                bad_locale = locale
            if locale is not None:
                break
        if bad_locale is not None:
            extra += (
                '\n\nnpm2deb discovered that you exported a UTF-8 locale\n'
                'but the locale system could not pick up from it because\n'
                'it does not exist.  The exported locale is "%s" but it\n'
                'is not supported'
            ) % bad_locale

    raise RuntimeError('npm2deb will abort further execution because Python 3 '
                       'was configured to use ASCII as encoding for the '
                       'environment.' + extra)
