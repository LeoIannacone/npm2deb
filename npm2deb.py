#!/usr/bin/python

from argparse import ArgumentParser
from npm2deb import Npm2Deb, utils, templates, helper, \
    DEBHELPER, STANDARDS_VERSION
from npm2deb.mapper import Mapper
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
    parser_create.add_argument('-l', '--license', default=None, \
        help='license used for debian files [default: the same of upstream]')
    parser_create.add_argument('-s', '--standards', default=STANDARDS_VERSION, \
        help='set standards-version [default: %(default)s]')
    parser_create.add_argument('node_module', \
        help='node module available via npm')
    parser_create.set_defaults(func=create)

    parser_view = subparsers.add_parser('view', \
        help="a summary view of a node module")
    parser_view.add_argument('node_module', \
        help='node module available via npm')
    parser_view.set_defaults(func=print_view)

    parser_depends = subparsers.add_parser('depends', \
        help='show module dependencies in npm and debian')
    parser_depends.add_argument('-r', '--recursive', action="store_true", \
        default=False, help='look for binary dependencies recursively')
    parser_depends.add_argument('-f', '--force', action="store_true", \
        default=False, help='force inspection for modules already in debian')
    parser_depends.add_argument('-b', '--binary', action="store_true", \
        default=False, help='show binary dependencies')
    parser_depends.add_argument('-B', '--builddeb', action="store_true", \
        default=False, help='show build dependencies')
    parser_depends.add_argument('node_module', \
        help='node module available via npm')
    parser_depends.set_defaults(func=show_dependencies)

    parser_rdepends = subparsers.add_parser('rdepends', \
        help='show the reverse dependencies for module')
    parser_rdepends.add_argument('node_module', \
        help='node module available via npm')
    parser_rdepends.set_defaults(func=show_reverse_dependencies)

    parser_search = subparsers.add_parser('search', \
        help="look for module in debian project")
    parser_search.add_argument('-b', '--bug', action="store_true", \
        default=False, help='search for existing bug in wnpp')
    parser_search.add_argument('-d', '--debian', action="store_true", \
        default=False, help='search for existing package in debian')
    parser_search.add_argument('-r', '--repository', action="store_true", \
        default=False, help='search for existing repository in alioth')
    parser_search.add_argument('node_module', \
        help='node module available via npm')
    parser_search.set_defaults(func=search_for_module)

    parser_itp = subparsers.add_parser('itp', \
        help="print a itp bug template")
    parser_itp.add_argument('node_module', \
        help='node module available via npm')
    parser_itp.set_defaults(func=print_itp)

    parser_license = subparsers.add_parser('license', \
        help='print license template and exit')
    parser_license.add_argument('-l', '--list', action="store_true", \
        default=False, help='show the available licenses')
    parser_license.add_argument('name', nargs='?', \
        help='the license name to show')
    parser_license.set_defaults(func=print_license)

    args = parser.parse_args()

    if args.debug:
        utils.DEBUG_LEVEL = args.debug

    helper.DO_PRINT = True
    args.func(args)

def search_for_module(args):
    # enable all by default
    if not args.bug and not args.debian and not args.repository:
        args.bug = True
        args.debian = True
        args.repository = True
    node_module = get_npm2deb_instance(args).name
    if args.debian:
        print("\nLooking for similiar package:")
        mapper = Mapper.get_instance()
        print("  %s" % mapper.get_debian_package(node_module)['repr'])
    if args.repository:
        print("")
        helper.search_for_repository(node_module)
    if args.bug:
        print("")
        helper.search_for_bug(node_module)
    print("")

    show_mapper_warnings()

def print_view(args):
    npm2deb_instance = get_npm2deb_instance(args)
    formatted = "{0:40}{1}"
    for key in ['name', 'version', 'description', 'homepage', 'license']:
        attr_key = key
        if key == 'license' or key == 'version':
            attr_key = 'upstream_%s' % key
        print(formatted.format("%s:" % key.capitalize(),
            getattr(npm2deb_instance, attr_key, None)))

    mapper = Mapper.get_instance()
    print(formatted.format("Debian:", mapper
        .get_debian_package(npm2deb_instance.name)['repr']))

    if mapper.has_warnings():
        print("")
        show_mapper_warnings()


def print_itp(args):
    get_npm2deb_instance(args).show_itp()

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

def show_dependencies(args):
    # enable all by default
    if not args.binary and not args.builddeb:
        args.binary = True
        args.builddeb = True

    npm2deb_instance = get_npm2deb_instance(args)
    module_name = npm2deb_instance.name
    json = npm2deb_instance.json

    if args.binary:
        if 'dependencies' in json and json['dependencies']:
            print "Dependencies:"
            helper.print_formatted_dependency("NPM", "Debian")
            module_ver = npm2deb_instance.upstream_version
            module_deb = Mapper.get_instance()\
                .get_debian_package(module_name)["repr"]
            helper.print_formatted_dependency("%s (%s)" % \
                (module_name, module_ver), module_deb)
            helper.search_for_dependencies(npm2deb_instance,
                args.recursive, args.force)
            print("")
        else:
            print("Module %s has no dependencies." % module_name)

    if args.builddeb:
        if 'devDependencies' in json and json['devDependencies']:
            print "Build dependencies:"
            helper.print_formatted_dependency("NPM", "Debian")
            helper.search_for_builddep(module_name)
            print("")
        else:
            print("Module %s has no build dependencies." % module_name)

    show_mapper_warnings()

def show_reverse_dependencies(args):
    node_module = get_npm2deb_instance(args).name
    helper.search_for_reverse_dependencies(node_module)

def create(args):
    npm2deb = get_npm2deb_instance(args)
    try:
        saved_path = os.getcwd()
        utils.create_dir(npm2deb.name)
        utils.change_dir(npm2deb.name)
        npm2deb.start()
        utils.change_dir(saved_path)
    except OSError as os_error:
        print(str(os_error))
        exit(1)

    debian_path = "%s/%s/debian" % (npm2deb.name, npm2deb.debian_name)

    print("""
This is not a crystal ball, so please take a look at auto-generated files.\n
You may want fix first these issues:\n""")
    call('/bin/grep --color=auto FIX_ME -r %s/*' % debian_path, shell=True)
    print ("\nUse uscan to get orig source files. Fix debian/watch and then run\
            \n$ uscan --download-current-version\n")

    show_mapper_warnings()


def check_module_name(args):
    if not args.node_module or len(args.node_module) is 0:
        print('please specify a node_module.')
        exit(1)
    return args.node_module

def get_npm2deb_instance(args):
    node_module = check_module_name(args)
    try:
        return Npm2Deb(node_module, vars(args))
    except ValueError as value_error:
        print value_error
        exit(0)

def show_mapper_warnings():
    mapper = Mapper.get_instance()
    if mapper.has_warnings():
        print("Warnings occured:")
        mapper.show_warnings()
        print("")

if __name__ == '__main__':
    main()
