# -*- coding: utf-8 -*-
from json import loads as parseJSON
from xml.dom import minidom
from npm2deb import Npm2Deb
from npm2deb.utils import debug
from npm2deb.mapper import Mapper
import re

try:
    from urllib.request import urlopen
    from subprocess import getstatusoutput
except ImportError:
    from commands import getstatusoutput
    from urllib2 import urlopen

DO_PRINT = False


def my_print(what):
    if DO_PRINT:
        print(what.encode('utf-8'))


def search_for_repository(module):
    if isinstance(module, Npm2Deb):
        module = module.name
    repositories = ['collab-maint', 'pkg-javascript']
    formatted = "  {0:40} -- {1}"
    found = False
    result = {}
    my_print("Looking for existing repositories:")
    for repo in repositories:
        debug(1, "search for %s in %s" % (module, repo))
        url_base = "http://anonscm.debian.org/gitweb"
        data = urlopen("%s/?a=project_list&pf=%s&s=%s" %
                      (url_base, repo, module)).read()
        dom = minidom.parseString(data)
        for row in dom.getElementsByTagName('tr')[1:]:
            try:
                columns = row.getElementsByTagName('td')
                name = columns[0].firstChild.getAttribute('href')\
                    .split('.git')[0].split('?p=')[1]
                description = columns[1].firstChild.getAttribute('title')
                found = True
                result[name] = description
                my_print(formatted.format(name, description))
            except:
                continue
    if not found:
        my_print("  None")
    return result


def search_for_bug(module):
    if isinstance(module, Npm2Deb):
        module = module.name
    my_print('Looking for wnpp bugs:')
    debug(1, "calling wnpp-check")
    info = getstatusoutput('wnpp-check %s' % module)
    if info[0] == 0:
        my_print('  None')
        return []
    else:
        lines = info[1].split('\n')
        formatted = "  #{0}  {1:>3}:  {2:25} -- {3}"
        result = []
        for line in lines:
            try:
                bug = {}
                bug['num'] = re.match('.*#(\d+).*\)', line).group(1)
                bug['type'] = re.match('\((\w+) .*', line).group(1)
                bug['package'] = re.match('.* (.*)$', line).group(1)
                bug['url'] = re.match('.* (.*) .*$', line).group(1)
                result.append(bug)
                my_print(formatted.format(bug["num"],
                                          bug["type"],
                                          bug["package"],
                                          bug["url"]))
            except:
                    continue
        return result


def search_for_reverse_dependencies(module):
    if isinstance(module, Npm2Deb):
        module = module.name
    url = "http://registry.npmjs.org/-/_view/dependedUpon?startkey=" \
        + "[%%22%(name)s%%22]&endkey=[%%22%(name)s%%22,%%7B%%7D]&group_level=2"
    url = url % {'name': module}
    debug(1, "opening url %s" % url)
    data = urlopen(url).read()
    data = parseJSON(data)
    result = []
    if 'rows' in data and len(data['rows']) > 0:
        my_print("Reverse Depends:")
        for row in data['rows']:
            dependency = row['key'][1]
            result.append(dependency)
            my_print("  %s" % dependency)
    else:
        my_print("Module %s has no reverse dependencies" % module)
    return result


def search_for_dependencies(module, recursive=False, force=False,
                            prefix=u'', expanded_dependencies=[]):
    try:
        if not isinstance(module, Npm2Deb):
            debug(1, 'getting dependencies - calling npm view %s' % module)
            npm_out = getstatusoutput('npm view "%s" '
                                      'dependencies --json 2>/dev/null'
                                      % module)[1]
            dependencies = parseJSON(npm_out)
        else:
            dependencies = module.json['dependencies']
            module = module.name
    except ValueError:
        return None

    mapper = Mapper.get_instance()
    result = {}

    keys = dependencies.keys()
    last_dep = False
    for dep in keys:
        if dep == keys[-1]:
            last_dep = True
        result[dep] = {}
        result[dep]['version'] = dependencies[dep]
        result[dep]['debian'] = mapper.get_debian_package(dep)['repr']
        dep_prefix = u'└─' if last_dep else u'├─'
        print_formatted_dependency(u"%s %s (%s)" % (dep_prefix, dep,
                                   result[dep]['version']),
                                   result[dep]['debian'], prefix)
        if recursive and not dep in expanded_dependencies:
            expanded_dependencies.append(dep)
            if (result[dep]['debian'] and force) or \
                    result[dep]['debian'] is None:
                new_prefix = "%s%s " % (prefix, u"  " if last_dep else u"│ ")
                result[dep]['dependencies'] = \
                    search_for_dependencies(dep, recursive, force, new_prefix,
                                            expanded_dependencies)
        else:
            result[dep]['dependencies'] = None

    return result


def search_for_builddep(module):
    try:
        if not isinstance(module, Npm2Deb):
            debug(1, 'getting builddep - calling npm view %s' % module)
            npm_out = getstatusoutput('npm view "%s" '
                                      'devDependencies --json 2>/dev/null'
                                      % module)[1]
            builddeb = parseJSON(npm_out)
        else:
            builddeb = module.json['devDependencies']
            module = module.name
    except ValueError:
        return None

    mapper = Mapper.get_instance()
    result = {}

    for dep in builddeb:
        result[dep] = {}
        result[dep]['version'] = builddeb[dep]
        result[dep]['debian'] = mapper.get_debian_package(dep)['repr']
        print_formatted_dependency("%s (%s)" % (dep, result[dep]['version']),
                                   result[dep]['debian'])

    return result


def print_formatted_dependency(npm, debian, prefix=u''):
    formatted = u"{0:50}{1}"
    my_print(formatted.format(u"%s%s" % (prefix, npm), debian))
