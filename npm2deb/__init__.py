from json import loads as _parseJSON
from datetime import datetime as _datetime
from dateutil import tz as _tz
from shutil import rmtree as _rmtree
from urllib.request import urlopen as _urlopen
from subprocess import getstatusoutput as _getstatusoutput
from subprocess import call as _call
import os as _os
import re as _re

from npm2deb import utils, templates
from npm2deb.mapper import Mapper

VERSION = '0.2.5'
DEBHELPER = 9
STANDARDS_VERSION = '3.9.8'


class Npm2Deb(object):

    def __init__(self, module_name=None, args={}):
        if not module_name and not 'node_module' in args:
            raise ValueError('You must specify a module_name')
        if module_name:
            self.name = module_name
        elif 'node_module' in args:
            self.name = args['node_module']
        self.json = None
        self.args = args
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
        self.uscan_info = ''
        if args:
            if 'upstream_license' in args and args['upstream_license']:
                self.upstream_license = args['upstream_license']
            if 'upstream_author' in args and args['upstream_author']:
                self.upstream_author = args['upstream_author']
            if 'upstream_homepage' in args and args['upstream_homepage']:
                self.homepage = args['upstream_homepage']
            if 'debian_license' in args and args['debian_license']:
                self.debian_license = args['debian_license']
            if 'standards_version' in args and args['standards_version']:
                self.debian_standards = args['standards_version']
            if 'debhelper' in args:
                self.debian_debhelper = args['debhelper']
            if 'noclean' in args:
                self.noclean = args['noclean']

        self.read_package_info()
        self.debian_name = 'node-%s' % utils.debianize_name(self.name)
        self.debian_author = 'FIX_ME debian author'
        if 'DEBFULLNAME' in _os.environ and 'DEBEMAIL' in _os.environ:
            self.debian_author = "%s <%s>" % \
                (_os.environ['DEBFULLNAME'], _os.environ['DEBEMAIL'])
        elif 'DEBFULLNAME' in _os.environ and 'EMAIL' in _os.environ:
            self.debian_author = "%s <%s>" % \
                (_os.environ['DEBFULLNAME'], _os.environ['EMAIL'])
        self.debian_dest = "usr/lib/nodejs/%s" % self.name
        self.date = _datetime.now(_tz.tzlocal())

    def start(self):
        self.download()
        utils.change_dir(self.debian_name)
        self.create_base_debian()
        self.create_tests()
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
        self.create_manpages()
        if not self.noclean:
            self.clean()
        utils.change_dir('..')
        self.create_itp_bug()

    def initiate_build(self ,saved_path):
        """
        Try building deb package after creating required files using start().
        'uscan', 'uupdate' and 'dpkg-buildpackage' are run if debian/watch is OK.
        """
        if self.uscan_info[0] == 0:
            self.run_uscan()
            
            remote_file_name = self.uscan_info[1].split(' ')[-1].split('/')[-1].replace('v','')
            tar_file_name = '%s-%s' % (self.debian_name, remote_file_name)
            self.run_uupdate(tar_file_name)
            
            compression_format = _re.search('\.(?:zip|tgz|tbz|txz|(?:tar\.(?:gz|bz2|xz)))', tar_file_name).group(0)
            new_dir_name = tar_file_name.replace(compression_format, '')
            utils.change_dir('../%s' % new_dir_name)
            self.run_buildpackage()

            self.edit_changelog()
            
            debian_path = "%s/%s/debian" % (self.name, new_dir_name)
            print ('\nRemember, your new source directory is %s/%s' % (self.name, new_dir_name))
            
        else:
            debian_path = "%s/%s/debian" % (self.name, self.debian_name)
        
        print("""
This is not a crystal ball, so please take a look at auto-generated files.\n
You may want fix first these issues:\n""")
        
        utils.change_dir(saved_path)
        _call('/bin/grep --color=auto FIX_ME -r %s/*' % debian_path, shell=True)

        if self.uscan_info[0] != 0:
            print ("\nUse uscan to get orig source files. Fix debian/watch and then run\
                    \n$ uscan --download-current-version\n")


    def edit_changelog(self):
        """
        This function is to remove extra line '* New upstream release' 
        from debian/changelog 
        """
        with open('debian/changelog', 'r') as f:
            data = f.read()
        f.close()
        
        data_list = data.split('\n')
        data_list.pop(3)

        with open('debian/changelog', 'w') as f:
            f.write('\n'.join(data_list))
        f.close()
        
    def run_buildpackage(self):
        print ("\nBuilding the binary package")
        _call('dpkg-source -b .', shell=True)
        _call('dpkg-buildpackage', shell=True)

    def run_uupdate(self, tar_file):
        print ('\nCreating debian source package...')
        _call('uupdate -b ../%s' % tar_file, shell=True)

    def run_uscan(self):
        print ('\nDownloading source tarball file using debian/watch file...')
        _os.system('uscan --download-current-version')
        
    def test_uscan(self):
        info = _getstatusoutput('uscan --watchfile "debian/watch" '
                                    '--package "{}" '
                                    '--upstream-version 0 --no-download'
                                    .format(self.debian_name))
        self.uscan_info = info

        
    def create_itp_bug(self):
        utils.debug(1, "creating wnpp bug template")
        utils.create_file('%s_itp.mail' % self.debian_name, self.get_ITP())

    def clean(self):
        utils.debug(1, "cleaning directory")
        for filename in _os.listdir('.'):
            if filename != 'debian':
                if _os.path.isdir(filename):
                    _rmtree(filename)
                else:
                    _os.remove(filename)

    def create_manpages(self):
        if 'man' in self.json:
            content = _os.path.normpath(self.json['man'])
            utils.create_debian_file('manpages', content)

    def create_watch(self):
        args = {}
        args['debian_name'] = self.debian_name
        args['dversionmangle'] = 's/\+(debian|dfsg|ds|deb)(\.\d+)?$//'
        args['url'] = self.upstream_repo_url
        args['module'] = self.name
        try:
            if self.upstream_repo_url.find('github') >= 0:
                content = utils.get_watch('github') % args
            else:
                # if not supported, got to fakeupstream
                raise ValueError

            utils.create_debian_file('watch', content)
            # test watch with uscan, raise exception if status is not 0
            self.test_uscan()
            
            if self.uscan_info[0] != 0:
                raise ValueError

        except ValueError:
            content = utils.get_watch('fakeupstream') % args
            utils.create_debian_file('watch', content)

    def create_examples(self):
        if _os.path.isdir('examples'):
            content = 'examples/*'
            utils.create_debian_file('examples', content)

    def create_dirs(self):
        if _os.path.isdir('bin'):
            content = 'usr/bin'
            utils.create_debian_file('dirs', content)

    def create_links(self):
        links = []
        dest = self.debian_dest
        if 'bin' in self.json:
            for script in self.json['bin']:
                orig = _os.path.normpath(self.json['bin'][script])
                links.append("%s/%s usr/bin/%s" %
                            (dest, orig, script))
        if len(links) > 0:
            content = '\n'.join(links)
            utils.create_debian_file('links', content)

    def create_install(self):
        content = ''
        libs = {'package.json'}
        if _os.path.isdir('bin'):
            libs.add('bin')
        if _os.path.isdir('lib'):
            libs.add('lib')

        # install files from directories field
        if 'directories' in self.json:
            directories = self.json['directories']
            if 'bin' in directories:
                libs.add(directories['bin'])
            if 'lib' in directories:
                libs.add(directories['lib'])

        # install files from files field
        if 'files' in self.json:
            libs = libs.union(self.json['files'])

        # install main if not in a subpath
        if 'main' in self.json:
            main = self.json['main']
            main = _os.path.normpath(main)
            if main == 'index':
                main = 'index.js'
            if not main.find('/') > 0:
                libs.add(_os.path.normpath(main))
        else:
            if _os.path.exists('index.js'):
                libs.add('index.js')
            else:
                libs.add('*.js')

        for filename in libs:
            content += "%s %s/\n" % (filename, self.debian_dest)
        utils.create_debian_file('install', content)

    def create_docs(self):
        docs = []
        if 'readmeFilename' in self.json and self.json['readmeFilename']:
            docs.append(self.json['readmeFilename'])
        else:
            for name in _os.listdir('.'):
                if name.lower().startswith('readme'):
                    docs.append(name)
                    break
        if len(docs) > 0:
            content = '\n'.join(docs)
            utils.create_debian_file('docs', content)

    def create_control(self):
        args = {}
        args['Source'] = self.debian_name
        args['Uploaders'] = self.debian_author
        args['debhelper'] = self.debian_debhelper
        args['Standards-Version'] = self.debian_standards
        args['Homepage'] = self.homepage
        args['Vcs-Git'] = 'https://anonscm.debian.org/' + \
                          'git/pkg-javascript/%s.git' \
                          % self.debian_name
        args['Vcs-Browser'] = 'https://anonscm.debian.org/' + \
                              'cgit/pkg-javascript/%s.git' \
                              % self.debian_name
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
        args['upstream_contact'] = self.upstream_author
        if 'bugs' in self.json and 'url' in self.json['bugs']:
            args['upstream_contact'] = self.json['bugs']['url']
        args['upstream_license_name'] = self.upstream_license
        if self.debian_license and \
                self.upstream_license != self.debian_license:
            args['upstream_license'] = "\nLicense: %s" % \
                utils.get_license(self.upstream_license)
        else:
            args['upstream_license'] = ''  # do not insert same license twice
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
        for filename in _os.listdir('.'):
            if filename.lower().startswith('history'):
                args['overrides'] += "override_dh_installchangelogs:\n" + \
                                     "\tdh_installchangelogs -k %s\n" % filename
                break
        content = utils.get_template('rules') % args
        utils.create_debian_file("rules", content)
        _os.system('chmod +x debian/rules')

    def create_tests(self):
        utils.create_dir("debian/tests")
        args = {}
        args['name'] = self.name
        args['debian_name'] = self.debian_name
        control = utils.get_template('tests/control') % args
        utils.create_debian_file("tests/control", control)
        require = utils.get_template("tests/require") % args
        utils.create_debian_file("tests/require", require)

    def create_base_debian(self):
        utils.debug(1, "creating debian files")
        utils.create_dir("debian")
        utils.create_dir("debian/source")
        utils.create_debian_file("source/format", "3.0 (quilt)\n")
        utils.create_debian_file("compat", self.debian_debhelper)

    def read_package_info(self):
        data = None
        name_is = None
        if _re.match("^(http:\/\/|https:\/\/)", self.name):
            utils.debug(1, "reading json - opening url %s" % self.name)
            data = _urlopen(self.name).read().decode('utf-8')
            name_is = 'url'

        elif _os.path.isfile(self.name):
            utils.debug(1, "reading json - opening file %s" % self.name)
            with open(self.name, 'r') as fd:
                data = fd.read()
            name_is = 'file'

        else:
            name_is = 'npm'
            utils.debug(1, "reading json - calling npm view %s" % self.name)
            info = _getstatusoutput('npm view "%s" --json 2>/dev/null' %
                                    self.name)
            # if not status 0, raise expection
            if info[0] != 0:
                info = _getstatusoutput('npm view "%s" --json' % self.name)
                exception = 'npm reports errors about %s module:\n' % self.name
                exception += info[1]
                raise ValueError(exception)
            if not info[1]:
                exception = 'npm returns empty json for %s module' % self.name
                raise ValueError(exception)
            data = info[1]

        try:
            self.json = _parseJSON(data)
        except ValueError as value_error:
            # if error during parse, try to fail graceful
            if str(value_error) == 'Expecting value: line 1 column 1 (char 0)':
                if name_is != 'npm':
                    raise ValueError("Data read from %s "
                                     "is not in a JSON format." % name_is)
                versions = []
                for line in data.split('\n'):
                    if _re.match(r"^[a-z](.*)@[0-9]", line):
                        version = line.split('@')[1]
                        versions.append(version)
                if len(versions) > 0:
                    exception = "More than one version found. "\
                        "Please specify one of:\n %s" % '\n '.join(versions)
                    raise ValueError(exception)
                else:
                    raise value_error
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
        info = _getstatusoutput('npm install "%s"' % self.name)
        if info[0] is not 0:
            exception = "Error downloading package %s\n" % self.name
            exception += info[1]
            raise ValueError(exception)
        # move dir from npm root
        root = _getstatusoutput('npm root')[1].strip('\n')
        _os.rename(_os.path.join(root, self.name), self.name)
        try:
            _os.rmdir(root)  # remove only if empty
        except OSError:
            pass
        # remove any dependency downloaded via npm
        if _os.path.isdir("%s/node_modules" % self.name):
            _rmtree("%s/node_modules" % self.name)
        if self.name is not self.debian_name:
            utils.debug(2, "renaming %s to %s" % (self.name, self.debian_name))
            _os.rename(self.name, self.debian_name)

    def get_ITP(self):
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
        if not self.upstream_license:
            self.upstream_license = "FIX_ME upstream license"
            license_name = None
            if 'licenses' in self.json:
                license_name = self.json['licenses']
            elif 'license' in self.json:
                license_name = self.json['license']
            if license_name:
                if isinstance(license_name, list):
                    license_name = license_name[0]
                if isinstance(license_name, dict):
                    license_name = license_name['type']
                if license_name.lower() == "mit":
                    license_name = "Expat"
                self.upstream_license = license_name
        if self.debian_license is None or \
           self.debian_license.find('FIX_ME') >= 0:
            self.debian_license = self.upstream_license

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
        if self.upstream_author:
            return
        result = 'FIX_ME upstream author'
        if 'author' in self.json:
            author = self.json['author']
            if isinstance(author, str):
                result = author
            elif isinstance(author, dict):
                if 'name' in author and 'email' in author:
                    result = "%s <%s>" % (author['name'], author['email'])
                elif 'name' in author:
                    result = author['name']
        self.upstream_author = result

    def _get_json_repo_url(self):
        result = 'FIX_ME repo url'
        url = None
        if 'repository' in self.json:
            repository = self.json['repository']
            if isinstance(repository, str):
                url = repository
            elif isinstance(repository, dict) and 'url' in repository:
                url = repository['url']

            if not url:
                pass            # repository field is not in expected format
            elif url.startswith('git') or (isinstance(repository, dict) and
                                         'type' in repository and
                                         repository['type'] == 'git'):
                if url.find('github') >= 0:
                    tmp = self._get_github_url_from_git(url)
                    if tmp:
                        result = tmp
                else:
                    url = _re.sub(r'^git@(.*):', r'http://\1/', url)
                    url = _re.sub(r'^git://', 'http://', url)
                    url = _re.sub(r'\.git$', '', url)
                    result = url
            else:
                result = url
        self.upstream_repo_url = result

    def _get_json_homepage(self):
        if self.homepage:
            return
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
                    mapper.append_warning('error', dep, 'dependency %s '
                                          'not in debian' % (name))
                version = dependencies[dep]
                if version:
                    version = version.lower().replace('~', '').replace('^', '').replace('.x', '.0')
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

    def _get_github_url_from_git(self, url):
        result = _getstatusoutput(
            "nodejs -e "
            "\"console.log(require('github-url-from-git')"
            "('%s'));\"" % url)[1]
        if result == 'undefined':
            result = None
        return result
