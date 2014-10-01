#!/usr/bin/env python2
import argparse
import json
import os
import subprocess
import urllib2

import pip

import jasperpath


MODULES_URL = 'http://jaspermoduleshub.herokuapp.com'


class ModuleTypeError(Exception):
    pass


def install(module):
    if _module_exists(module):
        metadata = _get_module_metadata(module)
        module_path = _get_module_folder(module)
        _download_module_files(metadata, module_path, module)
        _install_requirements(module_path)
        print "Installed module: %s" % module
    else:
        print "Sorry, that module could not be found"


def _module_exists(module):
    try:
        urllib2.urlopen(_module_url(module))
    except urllib2.HTTPError:
        return False
    else:
        return True


def _module_url(module):
    return MODULES_URL+'/plugins/%s.json' % module


def _get_module_metadata(module):
    response = urllib2.urlopen(_module_url(module))
    return json.loads(response.read())


def _get_module_folder(module):
    return os.path.join(jasperpath.PLUGIN_PATH, module)


def _download_module_files(metadata, module_path, module):
    file_type = metadata['last_version']['file_type']
    if file_type == 'git':
        _download_git(metadata, module_path)
    elif file_type == 'file':
        _download_single_file(metadata, module_path, module)
    else:
        raise ModuleTypeError(module)


def _download_git(metadata, module_path):
    filename = metadata['last_version']['file']
    subprocess.call(['git', 'clone', filename, module_path])


def _download_single_file(metadata, module_path, module):
    _create_module_folder(module_path)
    _download_file(metadata, module_path, module, '.py')


def _create_module_folder(module_path):
    if not os.path.exists(module_path):
        os.makedirs(module_path)
    open(os.path.join(module_path, '__init__.py'), 'a').close()


def _download_file(metadata, module_path, module, extension):
    filename = metadata['last_version']['file']
    module_code = urllib2.urlopen(filename).read()
    module_file = os.path.join(module_path, module + extension)
    with open(module_file, 'w') as file:
        file.write(module_code)


def _install_requirements(module_path):
    reqs_file = os.path.join(module_path, 'requirements.txt')
    if os.path.isfile(reqs_file):
        pip.main(['install', '-r', reqs_file])


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Jasper modules installer')
    parser.add_argument('--install', nargs='+',
                        help='Modules to install')

    args = parser.parse_args()
    for module in args.install:
        install(module)
