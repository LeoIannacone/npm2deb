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
    formatted = "  {0:40} | {1}"
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
        my_print("  no repo found.")
    return result

def search_for_bug(module_name, do_print=True):
    import SOAPpy
    global DO_PRINT
    DO_PRINT = do_print
    url = 'http://bugs.debian.org/cgi-bin/soap.cgi'
    server = SOAPpy.SOAPProxy(url, 'Debbugs/SOAP')
    bugs = server.get_bugs("package", "wnpp")
    found = False
    result = {}
    my_print("Inspecting %s reports on wnpp:" % len(bugs))
    statuses = server.get_status(bugs)
    for status in statuses:
        try:
            subject = status['item']['value']['subject']
            bug = status['item']['value']['bug_num']
            if subject.find(module_name) >= 0:
                found = True
                result[bug] = subject
                my_print("  #%s  %s" % (bug, subject))
        except:
            continue
    if not found:
        my_print("  no bug found.")
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
