from json import loads as _parseJSON
from re import findall as _findall
from urllib.request import urlopen as _urlopen
from subprocess import getstatusoutput as _getstatusoutput
from fnmatch import fnmatch as _fnmatch

from npm2deb.utils import debug as _debug
from npm2deb.utils import debianize_name as _debianize_name

DB_URL = 'https://wiki.debian.org/Javascript/Nodejs/Database'


class Mapper(object):
    INSTANCE = None

    def __init__(self):
        if self.INSTANCE is not None:
            raise ValueError("Mapper is a Singleton. "
                             "Please use get_instance method.")
        _debug(2, 'loading database from %s' % DB_URL)
        data = _findall(
            '{{{(.*)}}}',
            _urlopen("%s?action=raw" % DB_URL).read().decode('utf-8').replace(
                '\n', ''))[0]
        self.json = _parseJSON(data)
        self._warnings = {}
        self.reset_warnings()

    @classmethod
    def get_instance(cls):
        if cls.INSTANCE is None:
            cls.INSTANCE = Mapper()
        return cls.INSTANCE

    def get_debian_package(self, node_module):
        result = {}
        result['info'] = None
        result['name'] = None
        result['version'] = None
        result['suite'] = None
        result['repr'] = None
        db_package = None

        if node_module in self.json:
            db_package = self.json[node_module]
        else:
            for pattern in self.json.keys():
                if _fnmatch(node_module, pattern):
                    db_package = self.json[pattern]
                    break

        if db_package:
            if 'replace' in db_package:
                result['name'] = db_package['replace']
            if 'info' in db_package:
                result['info'] = ('info', db_package['info'])
                self.append_warning('info', node_module, db_package['info'])
            elif 'warning' in db_package:
                result['info'] = ('warning', db_package['warning'])
                self.append_warning('warning', node_module,
                                    db_package['warning'])
            elif 'error' in db_package:
                result['info'] = ('error', db_package['error'])
                self.append_warning('error', node_module, db_package['error'])
        else:
            result['name'] = 'node-%s' % _debianize_name(node_module)

        if not result['name']:
            return result

        madison = _getstatusoutput(
            'rmadison -u debian "%s" | tac | grep source' % result['name'])

        if madison[0] != 0:
            result['name'] = None
            return result

        tmp = madison[1].split('|')
        if len(tmp) >= 2:
            result['name'] = tmp[0].strip()
            result['version'] = tmp[1].strip()
            result['suite'] = tmp[2].strip()
            result['repr'] = '%s (%s)' % (result['name'], result['version'])

        return result

    def get_warnings(self, reset=True):
        result = self._warnings
        if reset:
            self.reset_warnings()
        return result

    def show_warnings(self, reset=True):
        for label in ['info', 'warning', 'error']:
            for name in self._warnings[label]:
                self._print_formatted_warning(label, name)
        if reset:
            self.reset_warnings()

    def has_warnings(self):
        if self._warnings['info'] or self._warnings['error'] or \
                self._warnings['warning']:
            return True
        return False

    def reset_warnings(self):
        self._warnings = {}
        self._warnings['info'] = {}
        self._warnings['error'] = {}
        self._warnings['warning'] = {}

    def append_warning(self, label, node_module, warning):
        self._warnings[label][node_module] = warning

    def _print_formatted_warning(self, label, name):
        formatted = ' {0:9} {1}: {2}'
        msg = self._warnings[label][name]
        print(formatted.format("[%s]" % label, name, msg))
