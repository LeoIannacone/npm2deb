#!/usr/bin/python

from json import loads as parseJSON
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
DEBIAN_LICENSE = 'GPL-3'

class Npm2Deb():

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

        # get first info
        getstatusoutput("npm view %s version" % package_name)
        self.debian_name = 'node-%s' % self._debianize_name(self.name)
        self.debian_author = 'FIX_ME'
        if 'DEBFULLNAME' in os.environ and 'DEBEMAIL' in os.environ:
            self.debian_author = "%s <%s>" % \
                (os.environ['DEBFULLNAME'], os.environ['DEBEMAIL'])
        elif 'DEBFULLNAME' in os.environ and 'EMAIL' in os.environ:
            self.debian_author = "%s <%s>" % \
                (os.environ['DEBFULLNAME'], os.environ['EMAIL'])
        self.debian_dest = "usr/lib/nodejs/%s" % self.name
        self.date = datetime.now(tz.tzlocal())
        self.read_package_info()

    def show_dependencies(self):
        if 'devDependencies' in self.json and self.json['devDependencies']:
            print "Build dependencies:"
            self._get_formatted_comparision_npm_deb(\
                    self.json['devDependencies'])
            print("")
        else:
            print("Module %s has no build dependencies." % self.name)

        if 'dependencies' in self.json and self.json['dependencies']:
            print "Dependencies:"
            self._get_formatted_comparision_npm_deb(\
                    self.json['dependencies'])
            print("")
        else:
            print("Module %s has no dependencies." % self.name)

    def show_reverse_dependencies(self):
        from urllib2 import urlopen
        url = "http://registry.npmjs.org/-/_view/dependedUpon?startkey=" \
        + "[%%22%(name)s%%22]&endkey=[%%22%(name)s%%22,%%7B%%7D]&group_level=2"
        url = url % {'name': self.name}
        utils.debug(1, "opening url %s" % url)
        data = urlopen(url).read()
        data = parseJSON(data)
        if 'rows' in data and len(data['rows']) > 0:
            print("Reverse Depends:")
            for row in data['rows']:
                print("  %s" % row['key'][1])
        else:
            print ("Module %s has no reverse dependencies" % self.name)

    def start(self):
        self.download()
        utils.change_dir(self.debian_name)
        self.create_base_debian()
        self.create_rules()
        self.create_changelog()
        self.create_copyright()
        self.create_control()
        self.create_docs()
        self.create_install()
        self.create_links()
        self.create_dirs()
        self.create_examples()
        self.create_watch()
        if not self.noclean:
            self.clean()
        utils.change_dir('..')
        self.create_itp_bug()

    def create_itp_bug(self):
        utils.debug(1, "creating wnpp bug template")
        args = {}
        args['debian_author'] = self.debian_author
        args['debian_name'] = self.debian_name
        args['upstream_author'] = self.upstream_author
        args['homepage'] = self.homepage
        args['description'] = self.description
        args['version'] = self.version
        args['license'] = self.license
        content = utils.get_template('wnpp')
        utils.create_file('%s_itp.mail' % self.debian_name, content % args)

    def clean(self):
        utils.debug(1, "cleaning directory")
        for filename in os.listdir('.'):
            if filename != 'debian':
                if os.path.isdir(filename):
                    rmtree(filename)
                else:
                    os.remove(filename)

    def create_watch(self):
        if self.homepage.find('github') >= 0:
            args = {}
            args['homepage'] = self.homepage
            args['debian_name'] = self.debian_name
            file_content = templates.WATCH_GITHUB % args
        else:
            file_content = '# FIX_ME Please take a look \
              at https://wiki.debian.org/debian/watch/\n'
            file_content += "Homepage is %s\n" % self.homepage
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
        content = ''
        dest = self.debian_dest
        if not os.path.isfile('index.js') and 'main' in self.json:
            content += "%s/%s %s/index.js\n" % (dest, \
                os.path.normpath(self.json['main']), dest)
        if os.path.isdir('bin'):
            for script in os.listdir('bin'):
                content += "%s/bin/%s usr/bin/%s" % \
                    (dest, script, script.replace('.js', ''))
        if len(content) > 0:
            utils.create_debian_file('links', content)

    def create_install(self):
        content = ''
        libs = ['package.json']
        if os.path.isdir('bin'):
            libs.append('bin')
        if os.path.isdir('lib'):
            libs.append('lib')
        # install main if not in a subpath
        if 'main' in self.json and \
            not self.json['main'].index('/') > 0:
            libs.append(os.path.normpath(self.json['main']))
        else:
            if os.path.exists('index.js'):
                libs.append('index.js')
            else:
                libs.append('*.js')
        for filename in libs:
            content += "%s %s/\n" % (filename, self.debian_dest)
        utils.create_debian_file('install', content)

    def create_docs(self):
        docs = []
        if 'readmeFilename' in self.json:
            docs.append(self.json['readmeFilename'])
        else:
            for name in os.listdir('.'):
                if name.lower().startswith('readme'):
                    docs.append(name)
                    break
        if len(docs) > 0:
            utils.create_debian_file('docs', '\n'.join(docs) + '\n')

    def create_control(self):
        args = {}
        args['Source'] = self.debian_name
        args['Uploaders'] = self.debian_author
        args['debhelper'] = self.debian_debhelper
        args['Standards-Version'] = self.debian_standards
        args['Homepage'] = self.homepage
        args['Vcs-Git'] = 'git://anonscm.debian.org/collab-maint/%s.git' \
           % self.debian_name
        args['Vcs-Browser'] = 'http://anonscm.debian.org/' + \
          'gitweb/?p=collab-maint/%s.git' % self.debian_name
        args['Package'] = self.debian_name
        args['Depends'] = self._get_Depends()
        args['Description'] = self.description
        args['Description_Long'] = 'FIX_ME long description'
        template = utils.get_template('control')
        utils.create_debian_file('control', template % args)

    def create_copyright(self):
        args = {}
        args['upstream_name'] = self.name
        args['source'] = self.homepage
        args['upstream_date'] = self.date.year
        args['upstream_author'] = self.upstream_author
        args['upstream_license_name'] = self.license
        args['upstream_license'] = utils.get_license(self.license)
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
        args['version'] = self.version
        args['date'] = self.date.strftime('%a, %d %b %Y %X %z')
        file_content = templates.CHANGELOG % args
        utils.create_debian_file("changelog", file_content)

    def create_rules(self):
        args = {}
        args['overrides'] = ''
        for filename in os.listdir('.'):
            if filename.lower().startswith('history'):
                args['overrides'] += \
                "override_dh_installchangelogs:\n" + \
                "\tdh_installchangelogs -k %s\n" % filename
                break
        content = utils.get_template('rules') % args
        utils.create_debian_file("rules", content)
        os.system('chmod +x debian/rules')

    def create_base_debian(self):
        utils.debug(1, "creating debian files")
        utils.create_dir("debian")
        utils.create_dir("debian/source")
        utils.create_debian_file("source/format", "3.0 (quilt)\n")
        utils.create_debian_file("compat", "%s\n" % self.debian_debhelper)

    def read_package_info(self):
        utils.debug(1, "reading package info using npm view")
        info = getstatusoutput('npm view %s --json' % self.name)
        # if not status 0, exit
        if info[0] != 0:
            print(info[1])
            exit(1)
        self.json = parseJSON(info[1])
        self._get_Author()
        self._get_Homepage()
        self._get_Description()
        self._get_Version()
        self._get_License()

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

    def _get_License(self):
        if 'license' in self.json:
            license_name = self.json['license']
            if license_name.lower() == "mit":
                license_name = "Expat"
            self.license = license_name
        else:
            self.license = "FIX_ME upstream license"

    def _get_Version(self):
        if 'version' in self.json:
            self.version = self.json['version']
        else:
            self.version = 'FIX_ME version'

    def _get_Description(self):
        if 'description' in self.json:
            self.description = self.json['description']
        else:
            self.description = 'FIX_ME description'

    def _get_Author(self):
        result = 'FIX_ME upstream author'
        if 'author' in self.json:
            author = self.json['author']
            if isinstance(author, (str, unicode)):
                result = author
            elif isinstance(author, dict):
                if 'name' in author and 'email' in author:
                    result = "%s <%s>" % (author['name'], author['email'])
                elif 'name' in author:
                    result = author['name']
        self.upstream_author = result

    def _get_Homepage(self):
        result = 'FIX_ME homepage'

        if 'homepage' in self.json:
            result = self.json['homepage']

        elif 'repository' in self.json:
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
        self.homepage = result

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

    def _get_formatted_comparision_npm_deb(self, module_list):
        formatted = "{0:40}{1}"
        print(formatted.format("NPM", "Debian"))
        for module_name in module_list:
            npmver = utils.get_npm_version(module_name)
            npminfo = "%s (%s)" % (module_name, npmver)
            debinfo = utils.get_debian_package(module_name)
            print(formatted.format(npminfo, debinfo))
