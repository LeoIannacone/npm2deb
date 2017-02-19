from argparse import ArgumentParser as _ArgumentParser
from subprocess import call as _call
import os as _os
import sys as _sys

from npm2deb import Npm2Deb as _Npm2Deb
from npm2deb import utils as _utils
from npm2deb import templates as _templates
from npm2deb import helper as _helper
from npm2deb import Mapper as _Mapper
import npm2deb as _


def main(argv=None):
    if not argv:
        argv = _sys.argv
    parser = _ArgumentParser(prog='npm2deb')
    parser.add_argument('-D', '--debug', type=int, help='set debug level')
    parser.add_argument(
        '-v', '--version', action='version',
        version='%(prog)s ' + _.VERSION)

    subparsers = parser.add_subparsers(title='commands')

    parser_create = subparsers.add_parser(
        'create',
        help='create the debian files')
    parser_create.add_argument(
        '-n', '--noclean', action="store_true",
        default=False, help='do not remove files downloaded with npm')
    parser_create.add_argument(
        '--debhelper', default=_.DEBHELPER,
        help='specify debhelper version [default: %(default)s]')
    parser_create.add_argument(
        '--standards-version', default=_.STANDARDS_VERSION,
        help='set standards-version [default: %(default)s]')
    parser_create.add_argument(
        '--upstream-author', default=None,
        help='set upstream author if not automatically recognized')
    parser_create.add_argument(
        '--upstream-homepage', default=None,
        help='set upstream homepage if not automatically recognized')
    parser_create.add_argument(
        '--upstream-license', default=None,
        help='set upstream license if not automatically recognized')
    parser_create.add_argument(
        '--debian-license', default=None,
        help='license used for debian files [default: the same of upstream]')
    parser_create.add_argument(
        'node_module',
        help='node module available via npm')
    parser_create.set_defaults(func=create)

    parser_view = subparsers.add_parser(
        'view',
        help="a summary view of a node module")
    parser_view.add_argument(
        '-j', '--json', action="store_true",
        default=False, help='print verbose information in json format')
    parser_view.add_argument(
        'node_module',
        help='node module available via npm')
    parser_view.set_defaults(func=print_view)

    parser_depends = subparsers.add_parser(
        'depends',
        help='show module dependencies in npm and debian')
    parser_depends.add_argument(
        '-r', '--recursive', action="store_true",
        default=False, help='look for binary dependencies recursively')
    parser_depends.add_argument(
        '-f', '--force', action="store_true",
        default=False, help='force inspection for modules already in debian')
    parser_depends.add_argument(
        '-b', '--binary', action="store_true",
        default=False, help='show binary dependencies')
    parser_depends.add_argument(
        '-B', '--builddeb', action="store_true",
        default=False, help='show build dependencies')
    parser_depends.add_argument(
        'node_module',
        help='node module available via npm')
    parser_depends.set_defaults(func=show_dependencies)

    parser_rdepends = subparsers.add_parser(
        'rdepends',
        help='show the reverse dependencies for module')
    parser_rdepends.add_argument(
        'node_module',
        help='node module available via npm')
    parser_rdepends.set_defaults(func=show_reverse_dependencies)

    parser_search = subparsers.add_parser(
        'search',
        help="look for module in debian project")
    parser_search.add_argument(
        '-b', '--bug', action="store_true",
        default=False, help='search for existing bug in wnpp')
    parser_search.add_argument(
        '-d', '--debian', action="store_true",
        default=False, help='search for existing package in debian')
    parser_search.add_argument(
        '-r', '--repository', action="store_true",
        default=False, help='search for existing repository in alioth')
    parser_search.add_argument(
        'node_module',
        help='node module available via npm')
    parser_search.set_defaults(func=search_for_module)

    parser_itp = subparsers.add_parser(
        'itp',
        help="print a itp bug template")
    parser_itp.add_argument(
        'node_module',
        help='node module available via npm')
    parser_itp.set_defaults(func=print_itp)

    parser_license = subparsers.add_parser(
        'license',
        help='print license template and exit')
    parser_license.add_argument(
        '-l', '--list', action="store_true",
        default=False, help='show the available licenses')
    parser_license.add_argument(
        'name', nargs='?',
        help='the license name to show')
    parser_license.set_defaults(func=print_license)

    if len(argv) == 1:
        parser.error("Please specify an option.")
    else:
        args = parser.parse_args(argv[1:])
        if args.debug:
            _utils.DEBUG_LEVEL = args.debug

        args.func(args)


def search_for_module(args):
    _helper.DO_PRINT = True
    # enable all by default
    if not (args.bug or args.debian or args.repository):
        args.bug = True
        args.debian = True
        args.repository = True
    node_module = get_npm2deb_instance(args).name
    if args.debian:
        print("\nLooking for similiar package:")
        mapper = _Mapper.get_instance()
        pkg_info = mapper.get_debian_package(node_module)
        print("  %s (%s)" % (pkg_info['repr'], pkg_info['suite']))
    if args.repository:
        print("")
        _helper.search_for_repository(node_module)
    if args.bug:
        print("")
        _helper.search_for_bug(node_module)
    print("")

    _show_mapper_warnings()


def print_view(args):
    npm2deb_instance = get_npm2deb_instance(args)
    if args.json:
        from json import dumps
        # print a clean version of json module
        json = npm2deb_instance.json
        for key in ['time', 'versions', 'dist-tags', 'component',
                    'users', 'time', 'maintainers', 'readmeFilename',
                    'contributors', 'keywords']:
            if key in json:
                del json[key]
        print(dumps(json, indent=4, sort_keys=True))

    else:
        formatted = "{0:40}{1}"
        for key in ['name', 'version', 'description', 'homepage', 'license']:
            attr_key = key
            if key == 'license' or key == 'version':
                attr_key = 'upstream_%s' % key
            print(formatted.format("%s:" % key.capitalize(),
                  getattr(npm2deb_instance, attr_key, None)))

        mapper = _Mapper.get_instance()
        pkg_info = mapper.get_debian_package(npm2deb_instance.name)
        print(formatted.format("Debian:",
                               "%s (%s)" % (pkg_info['repr'], pkg_info['suite'])))

        if mapper.has_warnings():
            print("")
            _show_mapper_warnings()


def print_itp(args):
    print(get_npm2deb_instance(args).get_ITP())


def print_license(args, prefix=""):
    if args.list:
        licenses = sorted(_templates.LICENSES.keys())
        print("%s Available licenses are: %s." %
              (prefix, ', '.join(licenses).lower()))
    else:
        if args.name is None:
            print("You have to specify a license name")
            args.list = True
            print_license(args)
        else:
            template_license = _utils.get_license(args.name)
            if not template_license.startswith('FIX_ME'):
                print(template_license)
            else:
                print("Wrong license name.")
                args.list = True
                print_license(args)


def show_dependencies(args):
    _helper.DO_PRINT = True
    # enable all by default
    if not args.binary and not args.builddeb:
        args.binary = True
        args.builddeb = True

    npm2deb_instance = get_npm2deb_instance(args)
    module_name = npm2deb_instance.name
    json = npm2deb_instance.json

    if args.binary:
        if 'dependencies' in json and json['dependencies']:
            print("Dependencies:")
            _helper.print_formatted_dependency("NPM", "Debian")
            module_ver = npm2deb_instance.upstream_version
            module_deb = _Mapper.get_instance()\
                .get_debian_package(module_name)["repr"]
            _helper.print_formatted_dependency("%s (%s)" %
                                              (module_name, module_ver),
                                               module_deb)
            _helper.search_for_dependencies(npm2deb_instance,
                                            args.recursive,
                                            args.force)
            print("")
        else:
            print("Module %s has no dependencies." % module_name)

    if args.builddeb:
        if 'devDependencies' in json and json['devDependencies']:
            print("Build dependencies:")
            _helper.print_formatted_dependency("NPM", "Debian")
            _helper.search_for_builddep(npm2deb_instance)
            print("")
        else:
            print("Module %s has no build dependencies." % module_name)

    _show_mapper_warnings()


def show_reverse_dependencies(args):
    _helper.DO_PRINT = True
    node_module = get_npm2deb_instance(args).name
    _helper.search_for_reverse_dependencies(node_module)


def create(args):
    npm2deb = get_npm2deb_instance(args)
    try:
        saved_path = _os.getcwd()
        _utils.create_dir(npm2deb.name)
        _utils.change_dir(npm2deb.name)
        npm2deb.start()
        _utils.change_dir(npm2deb.debian_name)
        npm2deb.initiate_build(saved_path)

    except OSError as os_error:
        print(str(os_error))
        exit(1)

    _show_mapper_warnings()


def get_npm2deb_instance(args):
    if not args.node_module or len(args.node_module) is 0:
        print('please specify a node_module.')
        exit(1)
    try:
        return _Npm2Deb(args=vars(args))
    except ValueError as value_error:
        print(value_error)
        exit(1)


def _show_mapper_warnings():
    mapper = _Mapper.get_instance()
    if mapper.has_warnings():
        print("Warnings occured:")
        mapper.show_warnings()
        print("")

if __name__ == '__main__':
    main()
