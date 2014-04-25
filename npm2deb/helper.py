from utils import debug

DO_PRINT=False

def my_print(what):
    if DO_PRINT:
        print(what)

def search_for_repository(module_name, do_print=True):
    from urllib2 import urlopen
    from xml.dom import minidom
    global DO_PRINT
    DO_PRINT = do_print
    repositories = ['collab-maint', 'pkg-javascript']
    formatted = "  {0:40} -- {1}"
    found = False
    result = {}
    my_print("Looking for existing repositories:")
    for repo in repositories:
        debug(1, "search for %s in %s" % (module_name, repo))
        url_base = "http://anonscm.debian.org/gitweb"
        data = urlopen("%s/?a=project_list&pf=%s&s=%s" %
            (url_base, repo, module_name)).read()
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

def search_for_bug(module_name, do_print=True):
    from urllib2 import urlopen
    from xml.dom import minidom
    global DO_PRINT
    DO_PRINT = do_print
    url = 'http://wnpp.debian.net/' \
    '?type%5B%5D=ITA&type%5B%5D=ITP&type%5B%5D=O&type%5B%5D=RFA' \
    '&type%5B%5D=RFH&type%5B%5D=RFP&project=&description=&owner%5B%5D=yes' \
    '&owner%5B%5D=no&col%5B%5D=type&col%5B%5D=description&sort=project'

    data = urlopen(url).read()
    rows = data.split('class="data_table">')[1].split('</table>')[0].split('\n')
    found = False
    formatted = "  #{0}  {1:>3}:  {2:25} -- {3}"
    result = []
    my_print('Looking for wnpp bugs:')
    for row in rows:
        row = row.replace('&nbsp;', '')
        if len(row) > 0:
            try:
                bug = {}
                dom = minidom.parseString(row)
                tmp = dom.getElementsByTagName('a')[0]
                bug["num"] = tmp.getAttribute('href').split('?bug=')[1]
                bug["package"] = tmp.childNodes[0].data
                tmp = dom.getElementsByTagName('td')[-1]
                bug["type"] = tmp.getAttribute('class')
                bug["description"] = tmp.childNodes[0].childNodes[0].data
                if bug["package"].find(module_name) >= 0 or \
                        bug["description"].find(module_name) >= 0:
                    found = True
                    result.append(bug)
                    #my_print("  #%(num)s  %(type)s: %(package)s " \
                    #"-- %(description)s" % bug)
                    my_print(formatted.format(bug["num"], \
                        bug["type"], bug["package"], bug["description"]))
            except:
                continue
    if not found:
        my_print('  None')
    return result

def search_for_reverse_dependencies(module_name, do_print=True):
    from urllib2 import urlopen
    from json import loads as parseJSON
    global DO_PRINT
    DO_PRINT = do_print
    url = "http://registry.npmjs.org/-/_view/dependedUpon?startkey=" \
    + "[%%22%(name)s%%22]&endkey=[%%22%(name)s%%22,%%7B%%7D]&group_level=2"
    url = url % {'name': module_name}
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
        my_print("Module %s has no reverse dependencies" % module_name)
    return result
