#!/usr/bin/env python2
import argparse
import os
import urllib2
import json
import subprocess
import jasperpath

class ModuleInstaller():
    MODULES_URL = 'http://jaspermoduleshub.herokuapp.com'
    def __init__(self, module):
        self.module = module
        self.PROCESS_FILE = {
                'file': self.download_single_file,
                'git': self.download_git
                }


    def install(self):
        if self.module_exists():
            self.get_module_metadata()
            self.module_path = os.path.join(jasperpath.PLUGIN_PATH, self.module)
            self.download_module_files()
            self.install_requirements()
            print "Installed module: %s" % self.module

    def create_module_folder(self):
        if not os.path.exists(self.module_path):
            os.makedirs(self.module_path)
        open(os.path.join(self.module_path, '__init__.py'), 'a').close()

    def module_exists(self):
        try:
            urllib2.urlopen(self.module_url())
        except urllib2.HTTPError:
            print "Sorry, that module could not be found"
            return False
        else:
            return True

    def module_url(self):
        return self.MODULES_URL+'/plugins/%s.json' % self.module

    def get_module_metadata(self):
        response = urllib2.urlopen(self.module_url())
        self.module_json = json.loads(response.read())

    def download_module_files(self):
        self.PROCESS_FILE[self.module_json['last_version']['file_type']]()

    def download_single_file(self):
        self.create_module_folder()
        self.download_file('.py')

    def download_git(self):
        subprocess.call(['git', 'clone', self.module_json['last_version']['file'], self.module_path])

    def download_file(self, extension):
        module_code = urllib2.urlopen(self.module_json['last_version']['file']).read()
        module_file = os.path.join(self.module_path, self.module + extension)
        with open(module_file, 'w') as file:
            file.write(module_code)

    def install_requirements(self):
        reqs_file = os.path.join(self.module_path, 'requirements.txt')
        if os.path.isfile(reqs_file):
            subprocess.call(['pip', 'install', '-r', reqs_file])

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Jasper modules installer')
    parser.add_argument('--install', nargs=1,
                        help='Modules to install')

    args = parser.parse_args()
    for module in args.install:
        ModuleInstaller(module).install()


