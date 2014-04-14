#!/usr/bin/python

from json import load as parseJSON
from datetime import datetime
from dateutil import tz
from shutil import rmtree
from npm2deb import utils
from npm2deb import templates
import os
import stat
import re

# python 3 import
try:
    from commands import getstatusoutput
except ImportError:
    from subprocess import getstatusoutput

DEBHELPER = 9
STANDARDS_VERSION = '3.9.5'
DEBIAN_LICENSE = 'GPL-3.0+'

class Npm2Deb ():

    def __init__(self, package_name, args):
        self.json = None
        self.name = package_name
        self.debian_license = DEBIAN_LICENSE
        self.debian_standards = STANDARDS_VERSION
        self.debian_debhelper = DEBHELPER
        self.noclean = False
        if args:
            if 'license' in args:
                self.debian_license = args['license']
            if 'standards' in args:
                self.debian_standards = args['standards']
            if 'debhelper' in args:
                self.debian_debhelper = args['debhelper']
            if 'noclean' in args:
                self.noclean = args['noclean']

        info = getstatusoutput('npm info %s --json' % package_name)
        # if not status 0, exit
        if info[0] != 0:
            print(info[1])
            exit(1)
        self.debian_name = 'node-%s' % self._debianize_name(self.name)
        self.debian_author = 'FIX_ME'
        if 'DEBFULLNAME' in os.environ and 'EMAIL' in os.environ:
            self.debian_author = "%s <%s>" % \
                (os.environ['DEBFULLNAME'], os.environ['EMAIL'])
        elif 'DEBEMAIL' in os.environ:
            self.debian_author = os.environ['DEBEMAIL']
        self.debian_dest = "usr/lib/nodejs/%s" % self.name
        self.date = datetime.now(tz.tzlocal())

    def start(self):
        self.download()
        utils.change_dir(self.debian_name)
        self.read_package_info()
        self.create_base_debian()
        self.create_changelog()
        self.create_copyright()
        self.create_control()
        self.create_docs()
        self.create_install()
        self.create_links()
        self.create_dir()
        self.create_examples()
        self.create_watch()
        if not self.noclean:
            self.clean()

    def clean(self):
        utils.debug(1, "cleaning directory")
        for filename in os.listdir('.'):
            if filename != 'debian':
                if os.path.isdir(filename):
                    rmtree(filename)
                else:
                    os.remove(filename)

    def create_watch(self):
        homepage = self._get_Homepage()
        if homepage.find('github') >= 0:
            args = {}
            args['homepage'] = homepage
            args['debian_name'] = self.debian_name
            file_content = templates.WATCH_GITHUB % args
        else:
            file_content = '# FIX_ME Please take a look \
              at https://wiki.debian.org/debian/watch/\n'
            file_content += "Homepage is %s\n" % homepage
        utils.create_debian_file('watch', file_content)

    def create_examples(self):
        if os.path.isdir('examples'):
            content = 'examples/*\n'
            utils.create_debian_file('examples', content)

    def create_dirs(self):
        if os.path.isdir('bin'):
            content = 'usr/bin'
            utils.create_debian_file('dirs', content)

    def create_links(self):
        if not os.path.isfile('index.js') and 'main' in self.json:
            dest = self.debian_dest
            content = "%s/%s %s/index.js\n" % (dest, \
                os.path.normpath(self.json['main']), dest)
            utils.create_debian_file('links', content)

    def create_install(self):
        content = ''
        if os.path.isdir('bin'):
            content += 'bin/* usr/bin/\n'
        libs = []
        if 'main' in self.json:
            libs.append(os.path.normpath(self.json['main']))
        else:
            libs.append('*.js')
        if os.path.isdir('lib'):
            libs.append('lib')
        for filename in libs:
            content += "%s %s/\n" % (filename, self.debian_dest)
        utils.create_debian_file('install', content)

    def create_docs(self):
        docs = ['package.json']
        if 'readmeFilename' in self.json:
            docs.append(self.json['readmeFilename'])
        else:
            for name in os.listdir('.'):
                if name.lower().startswith('readme'):
                    docs.append(name)
                    break
        utils.create_debian_file('docs', '\n'.join(docs) + '\n')

    def create_control(self):
        args = {}
        args['Source'] = self.debian_name
        args['Uploaders'] = self.debian_author
        args['debhelper'] = self.debian_debhelper
        args['Standards-Version'] = self.debian_standards
        args['Homepage'] = self._get_Homepage()
        args['Vcs-Git'] = 'git://anonscm.debian.org/collab-maint/%s.git' \
           % self.debian_name
        args['Vcs-Browser'] = 'http://anonscm.debian.org/' + \
          'gitweb/?p=collab-maint/%s.git' % self.debian_name
        args['Package'] = self.debian_name
        args['Depends'] = self._get_Depends()
        args['Description'] = 'FIX_ME'
        if 'description' in self.json:
            args['Description'] = self.json['description']
        args['Description_Long'] = 'FIX_ME long desciption'
        # if 'readme' in self.json:
        #     args['Description_Long'] = self.json['readme']
        template = utils.get_template('control')
        utils.create_debian_file('control', template % args)

    def create_copyright(self):
        args = {}
        args['upstream_name'] = self.name
        args['source'] = self._get_Homepage()
        args['upstream_date'] = self.date.year
        args['upstream_author'] = self._get_Author()
        args['upstream_license_name'] = 'FIX_ME specify upstream license name'
        args['upstream_license'] = 'FIX_ME specify upstream license description'
        if 'license' in self.json:
            license_name = self.json['license']
            if license_name.lower() == "mit":
                license_name = "Expat"
            args['upstream_license_name'] = license_name
            args['upstream_license'] = utils.get_license(license_name)
        args['debian_date'] = self.date.year
        args['debian_author'] = self.debian_author
        args['debian_license_name'] = self.debian_license
        args['debian_license'] = utils.get_license(self.debian_license)
        template = utils.get_template('copyright')
        utils.create_debian_file('copyright', template % args)

    def create_changelog(self):
        args = {}
        args['debian_author'] = self.debian_author
        args['debian_name'] = self.debian_name
        args['version'] = 'FIX_ME'
        if 'version' in self.json:
            args['version'] = self.json['version']
        args['date'] = self.date.strftime('%a, %d %b %Y %X %z')
        file_content = templates.CHANGELOG % args
        utils.create_debian_file("changelog", file_content)

    def create_base_debian(self):
        utils.debug(1, "creating debian files")
        utils.create_dir("debian")
        utils.create_dir("debian/source")
        utils.create_debian_file("source/format", "3.0 (quilt)\n")
        utils.create_debian_file("compat", "%s\n" % self.debian_debhelper)
        utils.create_debian_file("rules", utils.get_template('rules'))
        os.system('chmod +x debian/rules')

    def read_package_info(self):
        utils.debug(1, "reading package info from package.json")
        with open('package.json') as package_json:
            self.json = parseJSON(package_json)

    def download(self):
        utils.debug(1, "downloading %s using npm" % self.name)
        info = getstatusoutput('npm install %s' % self.name)
        if info[0] is not 0:
            print("Error downloading package %s", self.name)
            print(info[1])
            exit(1)
        # move dir from node_modules
        os.rename('node_modules/%s' % self.name, self.name)
        rmtree('node_modules')
        # remove debendences download by npm if exists
        if os.path.isdir("%s/node_modules" % self.name):
            rmtree("%s/node_modules" % self.name)
        if self.name is not self.debian_name:
            utils.debug(2, "renaming %s to %s" % (self.name, self.debian_name))
            os.rename(self.name, self.debian_name)

    def _get_Author(self):
        result = 'FIX_ME'
        if 'author' in self.json:
            author = self.json['author']
            if author.__class__ is str:
                result = author
            elif author.__class__ is dict:
                if 'name' in author and 'email' in author:
                    result = "%s <%s>" % (author['name'], author['email'])
                elif 'name' in author:
                    result = author['name']
        return result

    def _get_Homepage(self):
        result = 'FIX_ME'
        if 'repository' in self.json:
            repository = self.json['repository']
            if 'type' in repository and 'url' in repository:
                if repository['type'] == 'git':
                    url = repository['url']
                    url = re.sub(r'^git@(.*):', r'http://\1/', url)
                    url = re.sub(r'^git://', 'http://', url)
                    url = re.sub(r'\.git$', '', url)
                    result = url
                else:
                    result = repository['url']
        return result

    def _get_Depends(self):
        depends = ['nodejs']
        if 'dependencies' in self.json:
            dependencies = self.json['dependencies']
            for dep in dependencies:
                name = 'node-%s' % self._debianize_name(dep)
                version = dependencies[dep].replace('~', '')
                if version[0].isdigit():
                    version = '>= %s' % version
                elif version == '*' or version == 'latest':
                    version = None
                if version:
                    dep_debian = "%s (%s)" % (name, version)
                else:
                    dep_debian = name
                depends.append(dep_debian)

        return '\n , '.join(depends)

    def _debianize_name(self, name):
        return name.replace('_', '-')
