#!/usr/bin/python

from optparse import OptionParser
from npm2deb import Npm2Deb, utils, templates, \
    DEBHELPER, STANDARDS_VERSION, DEBIAN_LICENSE
from subprocess import call
import os

def main():
    usage = 'usage %prog [options] package_name'
    parser = OptionParser(usage) 

    parser.add_option('-d', '--debhelper', default=DEBHELPER, \
        help='specify debhelper version [default: %default]')
    parser.add_option('-l', '--license', default=DEBIAN_LICENSE, \
        help='license used for debian files [default: %default]')
    parser.add_option('-n', '--noclean', action="store_true", default=False, \
        help='do not remove files downloaded with npm')
    parser.add_option('-p', '--printlicense', \
        help='print license template and exit')
    parser.add_option('-s', '--standards', default=STANDARDS_VERSION, \
        help='set standards-version [default: %default]')
    parser.add_option('-D', '--debug', help='set debug level')

    opts, args = parser.parse_args()

    if opts.printlicense:
        template_license = utils.get_license(opts.printlicense)
        if not template_license.startswith('FIX_ME'):
            print(template_license)
            exit(0)
        else:
            print("License \"%s\" is not valid." % opts.printlicense)
            print("Use one of: %s" % ', '.join(templates.LICENSES.keys()).lower())
            print("Ignore case accepted.")
            exit(1)

    if len(args) is not 1:
        parser.error('Please specify a package_name.')
        exit(1)

    if opts.debug:
        try:
            utils.DEBUG_LEVEL = int(opts.debug)
        except ValueError:
            print("Error: debug level must be an integer.")
            exit(1)

    package_name = args[0]
    saved_path = os.getcwd()
    utils.create_dir(package_name)
    utils.change_dir(package_name)

    npm2deb = Npm2Deb(package_name, vars(opts))
    npm2deb.start()

    utils.change_dir(saved_path)

    debian_path = "%s/%s/debian" % (package_name, npm2deb.debian_name)

    print("""
This is not a crystal ball, so please take a look at auto-generated files.\n
You may want fix first these issues:\n""")
    call('/bin/grep --color=auto FIX_ME -r %s/*' % debian_path, shell=True)
    print ("\nUse uscan to get orig source files. Fix debian/watch and then run:\n\n" + 
      "$ uscan --download-current-version\n")


if __name__ == '__main__':
    main()
