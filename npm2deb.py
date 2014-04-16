#!/usr/bin/python

from argparse import ArgumentParser
from npm2deb import Npm2Deb, utils, templates, \
    DEBHELPER, STANDARDS_VERSION, DEBIAN_LICENSE
from subprocess import call
import os

def main():
    parser = ArgumentParser(prog='npm2deb')
    parser.add_argument('-D', '--debug', type=int, help='set debug level')

    subparsers = parser.add_subparsers(title='commands')

    parser_create = subparsers.add_parser('create', \
        help='create the debian files')
    parser_create.add_argument('-n', '--noclean', action="store_true", \
        default=False, help='do not remove files downloaded with npm')
    parser_create.add_argument('-d', '--debhelper', default=DEBHELPER, \
        help='specify debhelper version [default: %(default)s]')
    parser_create.add_argument('-l', '--license', default=DEBIAN_LICENSE, \
        help='license used for debian files [default: %(default)s]')
    parser_create.add_argument('-s', '--standards', default=STANDARDS_VERSION, \
        help='set standards-version [default: %(default)s]')
    parser_create.add_argument('node_module', \
        help='node module available via npm')
    parser_create.set_defaults(func=create)

    parser_license = subparsers.add_parser('license', \
        help='print license template and exit')
    parser_license.add_argument('-l', '--list', action="store_true", \
        default=False, help='show the available licenses')
    parser_license.add_argument('name', nargs='?', \
        help='the license name to show')
    parser_license.set_defaults(func=print_license)

    parser_depends = subparsers.add_parser('depends', \
        help='show module dependencies in npm and debian')
    parser_depends.add_argument('node_module', \
        help='node module available via npm')
    parser_depends.set_defaults(func=show_dependencies)

    parser_rdepends = subparsers.add_parser('rdepends', \
        help='show the reverse dependencies for module')
    parser_rdepends.add_argument('node_module', \
        help='node module available via npm')
    parser_rdepends.set_defaults(func=show_reverse_dependencies)

    args = parser.parse_args()

    if args.debug:
        utils.DEBUG_LEVEL = args.debug

    args.func(args)

def print_license(args, prefix=""):
    if args.list:
        print("%s Available licenses are: %s." % \
                (prefix, ', '.join(sorted(templates.LICENSES.keys())).lower()))
    else:
        if args.name is None:
            print("You have to specify a license name")
            args.list = True
            print_license(args)
        else:
            template_license = utils.get_license(args.name)
            if not template_license.startswith('FIX_ME'):
                print(template_license)
            else:
                print("Wrong license name.")
                args.list = True
                print_license(args)

def get_npm2deb_instance(args):
    if not args.node_module or len(args.node_module) is 0:
        parser.error('please specify a node_module.')
        exit(1)

    node_module = args.node_module
    return Npm2Deb(node_module, vars(args))

def show_dependencies(args):
    get_npm2deb_instance(args).show_dependencies()

def show_reverse_dependencies(args):
    get_npm2deb_instance(args).show_reverse_dependencies()

def create(args):
    npm2deb = get_npm2deb_instance(args)
    saved_path = os.getcwd()
    utils.create_dir(npm2deb.name)
    utils.change_dir(npm2deb.name)
    npm2deb.start()

    utils.change_dir(saved_path)

    debian_path = "%s/%s/debian" % (npm2deb.name, npm2deb.debian_name)

    print("""
This is not a crystal ball, so please take a look at auto-generated files.\n
You may want fix first these issues:\n""")
    call('/bin/grep --color=auto FIX_ME -r %s/*' % debian_path, shell=True)
    print ("\nUse uscan to get orig source files. Fix debian/watch and then run\
            \n\n$ uscan --download-current-version\n")


if __name__ == '__main__':
    main()
