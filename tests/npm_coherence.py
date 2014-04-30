import sys
import os
import inspect
current = os.path.dirname(os.path.abspath(
            inspect.getfile(inspect.currentframe()) + '/..'))
sys.path.append(current)

import unittest
from commands import getstatusoutput
from shutil import rmtree
from npm2deb import Npm2Deb, DEBHELPER

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


class debian(unittest.TestCase):

    def test_debhelper_default(self):
        n = Npm2Deb('parse-url')
        n.create_base_debian()
        n.create_control()
        debhelper = None
        with open('debian/control', 'r') as control:
            for line in control.readlines():
                if line.find('debhelper') >= 0:
                    debhelper = line.strip('\n')
                    break
        self.assertEqual(debhelper, ' debhelper (>= %s)' % DEBHELPER)

        compat = None
        with open('debian/compat', 'r') as compat_fd:
            compat = compat_fd.read().strip('\n')
        self.assertEqual(compat, str(DEBHELPER))

        rmtree('debian')

    def test_debhelper_as_argument(self):
        MY_DEBHELPER = DEBHELPER + 1
        n = Npm2Deb('parse-url', {'debhelper': MY_DEBHELPER})
        n.create_base_debian()
        n.create_control()
        debhelper = None
        with open('debian/control', 'r') as control:
            for line in control.readlines():
                if line.find('debhelper') >= 0:
                    debhelper = line.strip('\n')
                    break
        self.assertEqual(debhelper, ' debhelper (>= %s)' % MY_DEBHELPER)

        compat = None
        with open('debian/compat', 'r') as compat_fd:
            compat = compat_fd.read().strip('\n')
        self.assertEqual(compat, str(MY_DEBHELPER))

    def tearDown(self):
        if os.path.isdir('debian'):
            rmtree('debian')

if __name__ == '__main__':
    unittest.main()
