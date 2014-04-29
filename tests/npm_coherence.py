import sys
import os
import inspect
current = os.path.dirname(os.path.abspath(
            inspect.getfile(inspect.currentframe()) + '/..'))
sys.path.append(current)

import unittest
from npm2deb import Npm2Deb

class npm2deb_coherences(unittest.TestCase):

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


if __name__ == '__main__':
    unittest.main()
