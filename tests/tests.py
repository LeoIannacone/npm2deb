#!/usr/bin/python3

import sys
import os
import inspect
current = os.path.dirname(os.path.abspath(
                          inspect.getfile(
                              inspect.currentframe()) + '/..'))
sys.path.append(current)

import unittest
from shutil import rmtree
from npm2deb import Npm2Deb, DEBHELPER


class npm2deb_fails(unittest.TestCase):
    def test_init_no_npm_module(self):
        try:
            Npm2Deb('MODULE_NOT_IN_NPM')
            raise Exception
        except Exception as err:
            self.assertTrue(isinstance(err, ValueError))
            # must suggest type of failure
            self.assertTrue(str(err).find('npm reports errors about') >= 0)

    def test_init_module_multiple_version(self):
        try:
            Npm2Deb('socket.io@0.9.x')
            raise Exception
        except Exception as err:
            self.assertTrue(isinstance(err, ValueError))
            # must suggest type of failure
            self.assertTrue(str(err)
                            .find('More than one version found. '
                                  'Please specify one of:') >= 0)


class npm_coherences_license(unittest.TestCase):

    def test_upstream_license_as_str(self):
        n = Npm2Deb('parse-url')
        self.assertEqual(n.upstream_license, 'Expat')

    def test_upstream_license_as_dict(self):
        n = Npm2Deb('utils-merge')
        self.assertEqual(n.upstream_license, 'Expat')

    def test_upstream_license_as_list(self):
        n = Npm2Deb('amdefine')
        self.assertEqual(n.upstream_license, 'BSD')

    def test_upstream_license_as_argument(self):
        n = Npm2Deb('amdefine', {'upstream_license': 'MIT'})
        self.assertEqual(n.upstream_license, 'MIT')

    def test_upstream_license_equals_debian_license(self):
        n = Npm2Deb('parse-url')
        self.assertEqual(n.upstream_license, n.debian_license)

    def test_debian_license_as_argument(self):
        n = Npm2Deb('amdefine', {'debian_license': 'GPL-3'})
        self.assertEqual(n.debian_license, 'GPL-3')


class read_json(unittest.TestCase):

    def test_json_via_npm(self):
        n = Npm2Deb('serve-index')
        self.assertEqual(n.name, 'serve-index')

    def test_json_via_url(self):
        n = Npm2Deb('https://raw.githubusercontent.com/' +
                    'expressjs/serve-index/master/package.json')
        self.assertEqual(n.name, 'serve-index')

    def test_json_via_file(self):
        file_name = '/tmp/test_json_via_file'
        test_name = "test_name"
        with open(file_name, 'w') as fd:
            fd.write('{"name":"%s"}' % test_name)
        n = Npm2Deb(file_name)
        os.remove(file_name)
        self.assertEqual(n.name, test_name)


class debian(unittest.TestCase):

    def tearDown(self):
        if os.path.isdir('debian'):
            rmtree('debian')

    def _get_file_line(self, filename, what):
        result = None
        with open(filename, 'r') as file_fd:
            for line in file_fd.readlines():
                if line.find(what) >= 0:
                    result = line.strip('\n')
                    break
        return result

    def _get_debfile_line(self, debian_filename, what):
        return self._get_file_line('debian/%s' % debian_filename, what)

    def test_debhelper(self):
        n = Npm2Deb('parse-url')
        n.create_base_debian()
        n.create_control()
        self.assertEqual(self._get_debfile_line("control",
                                                " debhelper-compat ("), ' debhelper-compat (= %s)' % DEBHELPER)

    def test_debhelper_as_argument(self):
        MY_DEBHELPER = DEBHELPER + 1
        n = Npm2Deb('parse-url', {'debhelper': MY_DEBHELPER})
        n.create_base_debian()
        n.create_control()
        self.assertEqual(self._get_debfile_line("control", " debhelper-compat ("),
                         ' debhelper-compat (= %s)' % MY_DEBHELPER)

    def test_manpages(self):
        n = Npm2Deb('jade')
        n.create_base_debian()
        n.create_manpages()
        self.assertEqual(self._get_debfile_line(
            'manpages', 'jade.1'), "jade.1")

    def test_watch_github(self):
        n = Npm2Deb('serve-static')
        n.create_base_debian()
        n.create_watch()
        line = self._get_debfile_line('watch', '/tags')
        self.assertTrue(line is not None and len(line) > 0)

    def test_watch_npmregistry(self):
        # must create a npmregistry since we do not know about git url
        n = Npm2Deb('yg-panache')
        n.create_base_debian()
        n.create_watch()
        line = self._get_debfile_line('watch', '/npmregistry')
        self.assertTrue(line is not None and len(line) > 0)

    def test_watch_github_with_no_tags(self):
        # must fallback on npmregistry if no tags in github
        n = Npm2Deb('security')
        n.create_base_debian()
        n.create_watch()
        line = self._get_debfile_line('watch', '/npmregistry')
        self.assertTrue(line is not None and len(line) > 0)

    def test_repository_defined_as_string(self):
        n = Npm2Deb('ipaddr.js')
        self.assertEqual(n.upstream_repo_url,
                         'https://github.com/whitequark/ipaddr.js')

    def test_install_bin(self):
        n = Npm2Deb('mocha')
        n.create_base_debian()
        n.create_links()
        line = self._get_debfile_line('links', 'mocha')
        self.assertEqual(line, 'usr/lib/nodejs/mocha/bin/mocha usr/bin/mocha')

    def test_write_tests(self):
        n = Npm2Deb('debug')
        n.create_base_debian()
        n.create_tests()
        line = self._get_debfile_line('tests/control', 'node-debug')
        self.assertEqual(line, 'Depends: node-debug')
        line = self._get_debfile_line('tests/require', 'debug')
        self.assertEqual(line, """node -e "require('debug');\"""")

    # Issues fixed
    def test_issue_10(self):
        n = Npm2Deb('lastfm')
        n.create_base_debian()
        n.create_control()

    def test_parse_name(self):
        n = Npm2Deb('jade@1.11.0')
        self.assertEqual(n.name, "jade")
        x = Npm2Deb('@ava/write-file-atomic')
        self.assertEqual(x.name, '@ava/write-file-atomic')
        y = Npm2Deb('@types/jquery@2.0.49')
        self.assertEqual(y.name, '@types/jquery')
        z = Npm2Deb('@types/jquery')
        self.assertEqual(z.name, '@types/jquery')



if __name__ == '__main__':
    unittest.main()
