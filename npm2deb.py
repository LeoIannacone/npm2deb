#!/usr/bin/python

from argparse import ArgumentParser
from npm2deb import Npm2Deb, utils, templates, \
    DEBHELPER, STANDARDS_VERSION, DEBIAN_LICENSE
from subprocess import call
import os
import sys

def main():
    usage = "%(prog)s [options] node_module | -p [license]"
    parser = ArgumentParser(prog='npm2deb', usage=usage)
    group = parser.add_mutually_exclusive_group()

    parser.add_argument('-s', '--show', action="store_true",
        default=False, help='show package dependencies in npm and debian')
    parser.add_argument('-n', '--noclean', action="store_true", \
        default=False, help='do not remove files downloaded with npm')
    group.add_argument('-p', '--printlicense', nargs='?', \
        help='print license template and exit')
    parser.add_argument('--debhelper', default=DEBHELPER, \
        help='specify debhelper version [default: %(default)s]')
    parser.add_argument('--license', default=DEBIAN_LICENSE, \
        help='license used for debian files [default: %(default)s]')
    parser.add_argument('--standards', default=STANDARDS_VERSION, \
        help='set standards-version [default: %(default)s]')
    parser.add_argument('-D', '--debug', type=int, help='set debug level')
    group.add_argument('node_module', nargs='?', \
        help='node module available via npm')

    opts = parser.parse_args()

    if '-p' in sys.argv or '--printlicense' in sys.argv:
        try:
            if opts.printlicense is None:
                raise ValueError
            template_license = utils.get_license(opts.printlicense)
            if not template_license.startswith('FIX_ME'):
                print(template_license)
                exit(0)
            else:
                print("License \"%s\" is not valid." % opts.printlicense)
                raise ValueError
        except ValueError:
            print("Available licenses are: %s" % \
                ', '.join(sorted(templates.LICENSES.keys())).lower())
            print("Ignore case accepted.")
            exit(1)

    if not opts.node_module or len(opts.node_module) is 0:
        parser.error('please specify a node_module.')
        exit(1)

    if opts.debug:
        utils.DEBUG_LEVEL = int(opts.debug)

    node_module = opts.node_module
    npm2deb = Npm2Deb(node_module, vars(opts))

    if opts.show:
        npm2deb.show_dependencies()
        exit(0)
    
    saved_path = os.getcwd()
    utils.create_dir(node_module)
    utils.change_dir(node_module)
    npm2deb.start()

    utils.change_dir(saved_path)

    debian_path = "%s/%s/debian" % (node_module, npm2deb.debian_name)

    print("""
This is not a crystal ball, so please take a look at auto-generated files.\n
You may want fix first these issues:\n""")
    call('/bin/grep --color=auto FIX_ME -r %s/*' % debian_path, shell=True)
    print ("\nUse uscan to get orig source files. Fix debian/watch and then run\
            \n\n$ uscan --download-current-version\n")


if __name__ == '__main__':
    main()
