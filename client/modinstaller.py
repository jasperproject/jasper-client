#!/usr/bin/env python2
import argparse
import os
import urllib2
import json
import subprocess
import jasperpath
import pip

class ModuleInstaller():
    MODULES_URL = 'http://jaspermoduleshub.herokuapp.com'
    def __init__(self, module):
        self.module = module
        self.PROCESS_FILE = {
                'file': self._download_single_file,
                'git': self._download_git
                }


    def install(self):
        if self._module_exists():
            self._get_module_metadata()
            self._module_path = os.path.join(jasperpath.PLUGIN_PATH, self.module)
            self._download_module_files()
            self._install_requirements()
            print "Installed module: %s" % self.module

    def _create_module_folder(self):
        if not os.path.exists(self._module_path):
            os.makedirs(self._module_path)
        open(os.path.join(self._module_path, '__init__.py'), 'a').close()

    def _module_exists(self):
        try:
            urllib2.urlopen(self._module_url())
        except urllib2.HTTPError:
            print "Sorry, that module could not be found"
            return False
        else:
            return True

    def _module_url(self):
        return self.MODULES_URL+'/plugins/%s.json' % self.module

    def _get_module_metadata(self):
        response = urllib2.urlopen(self._module_url())
        self._module_json = json.loads(response.read())

    def _download_module_files(self):
        self.PROCESS_FILE[self._module_json['last_version']['file_type']]()

    def _download_single_file(self):
        self._create_module_folder()
        self._download_file('.py')

    def _download_git(self):
        subprocess.call(['git', 'clone', self._module_json['last_version']['file'], self._module_path])

    def _download_file(self, extension):
        module_code = urllib2.urlopen(self._module_json['last_version']['file']).read()
        module_file = os.path.join(self._module_path, self.module + extension)
        with open(module_file, 'w') as file:
            file.write(module_code)

    def _install_requirements(self):
        reqs_file = os.path.join(self._module_path, 'requirements.txt')
        if os.path.isfile(reqs_file):
            pip.main(['install', '-r', reqs_file])

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Jasper modules installer')
    parser.add_argument('--install', nargs=1,
                        help='Modules to install')

    args = parser.parse_args()
    for module in args.install:
        ModuleInstaller(module).install()


