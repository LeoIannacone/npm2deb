#!/usr/bin/python

from json import loads as parseJSON
from datetime import datetime
from dateutil import tz
from shutil import rmtree
import os
import stat
import re

# python 3 import
try:
    from commands import getstatusoutput
except ImportError:
    from subprocess import getstatusoutput

from npm2deb import utils, templates
from npm2deb.mapper import Mapper

VERSION = '0.1.0'
DEBHELPER = 9
STANDARDS_VERSION = '3.9.5'

class Npm2Deb(object):

    def __init__(self, package_name, args={}):
        self.name = package_name
        self.args = args
        self.json = None
        self.homepage = None
        self.description = None
        self.upstream_author = None
        self.upstream_license = None
        self.upstream_version = None
        self.upstream_repo_url = None
        self.debian_license = "FIX_ME debian license"
        self.debian_standards = STANDARDS_VERSION
        self.debian_debhelper = DEBHELPER
        self.noclean = False
        if args:
            if 'license' in args and args['license']:
                self.debian_license = args['license']
            if 'standards' in args:
                self.debian_standards = args['standards']
            if 'debhelper' in args:
                self.debian_debhelper = args['debhelper']
            if 'noclean' in args:
                self.noclean = args['noclean']

        self.debian_name = 'node-%s' % self._debianize_name(self.name)
        self.debian_author = 'FIX_ME debian author'
        if 'DEBFULLNAME' in os.environ and 'DEBEMAIL' in os.environ:
            self.debian_author = "%s <%s>" % \
                (os.environ['DEBFULLNAME'].decode('utf-8')
                    , os.environ['DEBEMAIL'].decode('utf-8'))
        elif 'DEBFULLNAME' in os.environ and 'EMAIL' in os.environ:
            self.debian_author = "%s <%s>" % \
                (os.environ['DEBFULLNAME'].decode('utf-8'),
                    os.environ['EMAIL'].decode('utf-8'))
        self.debian_dest = "usr/lib/nodejs/%s" % self.name
        self.date = datetime.now(tz.tzlocal())
        self.read_package_info()

    def show_itp(self):
        print self._get_ITP()

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
        utils.create_file('%s_itp.mail' % self.debian_name, self._get_ITP())

    def clean(self):
        utils.debug(1, "cleaning directory")
        for filename in os.listdir('.'):
            if filename != 'debian':
                if os.path.isdir(filename):
                    rmtree(filename)
                else:
                    os.remove(filename)

    def create_watch(self):
        args = {}
        if self.upstream_repo_url and \
                self.upstream_repo_url.find('github') >= 0:
            args['homepage'] = self.upstream_repo_url
            args['debian_name'] = self.debian_name
            content = templates.WATCH_GITHUB % args
        else:
            content = "# FIX_ME Please take a look " \
                "at https://wiki.debian.org/debian/watch/\n" \
                "Homepage is %s\n" % self.homepage
        utils.create_debian_file('watch', content)

    def create_examples(self):
        if os.path.isdir('examples'):
            content = 'examples/*\n'
            utils.create_debian_file('examples', content)

    def create_dirs(self):
        if os.path.isdir('bin'):
            content = 'usr/bin'
            utils.create_debian_file('dirs', content)

    def create_links(self):
        links = []
        dest = self.debian_dest
        if os.path.isdir('bin'):
            for script in os.listdir('bin'):
                links.append("%s/bin/%s usr/bin/%s" % \
                    (dest, script, script.replace('.js', '')))
        if len(links) > 0:
            content = '\n'.join(links)
            utils.create_debian_file('links', content)

    def create_install(self):
        content = ''
        libs = ['package.json']
        if os.path.isdir('bin'):
            libs.append('bin')
        if os.path.isdir('lib'):
            libs.append('lib')
        # install main if not in a subpath
        if 'main' in self.json:
            main = self.json['main']
            main = os.path.normpath(main)
            if main == 'index':
                main = 'index.js'
            if not main.find('/') > 0:
                libs.append(os.path.normpath(main))
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
            content = '\n'.join(docs) + '\n'
            utils.create_debian_file('docs', content)

    def create_control(self):
        args = {}
        args['Source'] = self.debian_name
        args['Uploaders'] = self.debian_author
        args['debhelper'] = self.debian_debhelper
        args['Standards-Version'] = self.debian_standards
        args['Homepage'] = self.homepage
        args['Vcs-Git'] = 'git://anonscm.debian.org/pkg-javascript/%s.git' \
           % self.debian_name
        args['Vcs-Browser'] = 'http://anonscm.debian.org/' + \
          'gitweb/?p=pkg-javascript/%s.git' % self.debian_name
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
        args['upstream_license_name'] = self.upstream_license
        if self.debian_license and \
                self.upstream_license != self.debian_license:
            args['upstream_license'] = "\nLicense: %s" % \
                utils.get_license(self.upstream_license)
        else:
            args['upstream_license'] = '' # do not insert same license twice
        args['debian_date'] = self.date.year
        args['debian_author'] = self.debian_author
        args['debian_license_name'] = self.debian_license
        args['debian_license'] = "License: %s" % \
            utils.get_license(self.debian_license)
        template = utils.get_template('copyright')
        utils.create_debian_file('copyright', template % args)

    def create_changelog(self):
        args = {}
        args['debian_author'] = self.debian_author
        args['debian_name'] = self.debian_name
        args['version'] = self.upstream_version
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
        info = getstatusoutput('npm view %s --json 2>/dev/null' % self.name)
        # if not status 0, raise expection
        if info[0] != 0:
            info = getstatusoutput('npm view %s --json' % self.name)
            result = 'npm reports error about %s module:\n' % self.name
            result += info[1]
            raise ValueError(result)
        try:
            self.json = parseJSON(info[1])
        except ValueError as value_error:
            # if error during parse, try to fail graceful
            if str(value_error) == 'No JSON object could be decoded':
                versions = []
                for line in info[1].split('\n'):
                    if re.match("^[a-zA-Z]+@[0-9]", line):
                        version = line.split('@')[1]
                        versions.append(version)
                if len(versions) > 0:
                    result = "More than one version found. "\
                        "Please specify one of:\n %s" % '\n '.join(versions)
                    raise ValueError(result)
            else:
                raise value_error

        self.name = self.json['name']
        self._get_json_author()
        self._get_json_repo_url()
        self._get_json_homepage()
        self._get_json_description()
        self._get_json_version()
        self._get_json_license()

    def download(self):
        utils.debug(1, "downloading %s via npm" % self.name)
        info = getstatusoutput('npm install %s' % self.name)
        if info[0] is not 0:
            result = "Error downloading package %s\n" % self.name
            result += info[1]
            raise ValueError(result)
        # move dir from node_modules
        os.rename('node_modules/%s' % self.name, self.name)
        rmtree('node_modules')
        # remove any dependency downloaded via npm
        if os.path.isdir("%s/node_modules" % self.name):
            rmtree("%s/node_modules" % self.name)
        if self.name is not self.debian_name:
            utils.debug(2, "renaming %s to %s" % (self.name, self.debian_name))
            os.rename(self.name, self.debian_name)

    def _get_ITP(self):
        args = {}
        args['debian_author'] = self.debian_author
        args['debian_name'] = self.debian_name
        args['upstream_author'] = self.upstream_author
        args['homepage'] = self.homepage
        args['description'] = self.description
        args['version'] = self.upstream_version
        args['license'] = self.upstream_license
        content = utils.get_template('wnpp')
        return content % args

    def _get_json_license(self):
        if 'license' in self.json:
            license_name = self.json['license']
            if isinstance(license_name, dict):
                license_name = license_name['type']
            if license_name.lower() == "mit":
                license_name = "Expat"
            self.upstream_license = license_name
            if self.debian_license is None or \
                self.debian_license.find('FIX_ME') >= 0:
                self.debian_license = self.upstream_license
        else:
            self.upstream_license = "FIX_ME upstream license"

    def _get_json_version(self):
        if 'version' in self.json:
            self.upstream_version = self.json['version']
        else:
            self.upstream_version = 'FIX_ME version'

    def _get_json_description(self):
        if 'description' in self.json:
            self.description = self.json['description']
        else:
            self.description = 'FIX_ME description'

    def _get_json_author(self):
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

    def _get_json_repo_url(self):
        result = 'FIX_ME repo url'
        if 'repository' in self.json:
            repository = self.json['repository']
            if 'type' in repository and 'url' in repository:
                url = repository['url']
                if repository['type'] == 'git':
                    if url.find('github') >= 0:
                        tmp = self._get_github_url_from_git(url)
                        if tmp:
                            result = tmp
                    else:
                        url = re.sub(r'^git@(.*):', r'http://\1/', url)
                        url = re.sub(r'^git://', 'http://', url)
                        url = re.sub(r'\.git$', '', url)
                        result = url
                else:
                    result = url
        self.upstream_repo_url = result

    def _get_json_homepage(self):
        result = 'FIX_ME homepage'
        if 'homepage' in self.json:
            result = self.json['homepage']
        elif self.upstream_repo_url and not \
                self.upstream_repo_url.find('FIX_ME') >= 0:
            result = self.upstream_repo_url
        self.homepage = result

    def _get_Depends(self):
        depends = ['nodejs']
        mapper = Mapper.get_instance()
        if 'dependencies' in self.json:
            dependencies = self.json['dependencies']
            for dep in dependencies:
                name = mapper.get_debian_package(dep)['name']
                if not name:
                    name = 'node-%s' % dep
                    mapper.append_warning('error', dep, 'dependency %s '\
                        'not in debian' % (name))
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

    def _get_github_url_from_git(self, url):
        result = getstatusoutput("nodejs -e "
            "\"console.log(require('github-url-from-git')"
            "('%s'));\"" % url)[1]
        if result == 'undefined':
            result = None
        return result
