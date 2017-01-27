#!/usr/bin/env python2
import argparse
import os
import shutil
import subprocess
import tempfile
import urllib

import pip
import requests

import jasperpath


MODULES_URL = 'http://jaspermoduleshub.herokuapp.com/plugins/%s.json'


class ModuleInstallationError(Exception):
    def __init__(self, message, module):
        self.message = message
        self.module = module

    def __str__(self):
        return "%s: %s" % (self.message, self.module)


def install(module, install_location, install_dependencies):
    temp_path = _get_temp_module_folder(module)
    try:
        _check_installation_path(module, install_location)
        _download_module_files(temp_path, module)
        if install_dependencies:
            _install_requirements(temp_path)
        else:
            _list_unmet_requirements(module, temp_path)
        _copy_module_directory(temp_path, module, install_location)
    finally:
        _remove_temp_directory(temp_path)


def _module_url(module):
    return MODULES_URL % urllib.quote(module)


def _check_installation_path(module, install_location):
    module_path = _get_module_folder(module, install_location)
    if os.path.exists(module_path):
        raise ModuleInstallationError('Module folder already exists', module)
    if not os.access(install_location, os.W_OK):
        raise ModuleInstallationError('Location is not writable', module)


def _get_module_folder(module, install_location):
    return os.path.join(install_location, module)


def _get_module_metadata(module):
    try:
        response = requests.get(_module_url(module))
        response.raise_for_status()
    except requests.exceptions.HTTPError:
        raise ModuleInstallationError("The module could not be found", module)
    else:
        return response.json()


def _get_temp_module_folder(module):
    return tempfile.mkdtemp(prefix=module)


def _copy_module_directory(tmp_path, module, install_location):
    module_path = _get_module_folder(module, install_location)
    shutil.copytree(tmp_path, module_path)


def _download_module_files(module_path, module):
    metadata = _get_module_metadata(module)
    file_type = metadata['last_version']['file_type']
    if file_type == 'git':
        _download_git(metadata, module_path)
    elif file_type == 'file':
        _download_single_file(metadata, module_path, module)
    else:
        raise ModuleInstallationError("Invalid file type", module)


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
    module_file = os.path.join(module_path, module + extension)
    urllib.urlretrieve(filename, module_file)


def _install_requirements(module_path):
    reqs_file = os.path.join(module_path, 'requirements.txt')
    if os.path.isfile(reqs_file):
        pip.main(['install', '-r', reqs_file])


def _list_unmet_requirements(module, module_path):
    req_file = os.path.join(module_path, 'requirements.txt')
    if os.access(req_file, os.R_OK):
        missing_reqs = [req
                        for req in pip.req.parse_requirements(req_file)
                        if not req.check_if_exists()]
        if missing_reqs:
            print("PIP requirements missing for module %s:" % module)
            for req in missing_reqs:
                print(" - %s" % req.name)


def _remove_temp_directory(temp_path):
    shutil.rmtree(temp_path)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Jasper modules installer')
    parser.add_argument('--install', nargs='+',
                        help='Modules to install')
    parser.add_argument('--location', default=jasperpath.PLUGIN_PATH,
                        help="The location to install the modules to")
    parser.add_argument('--install-dependencies', default=False,
                        help="Install required dependencies")

    args = parser.parse_args()
    for module in args.install:
        try:
            install(module,
                    install_location=args.location,
                    install_dependencies=args.install_dependencies)
        except ModuleInstallationError as e:
            print e
        else:
            print "Installed module: %s" % module
