#!/usr/bin/env python2
import time
import re
import socket
import os
import jasperpath
import subprocess
import logging
import sys
from distutils.spawn import find_executable
from pip.req import parse_requirements
from pip.commands.show import search_packages_info

logger = logging.getLogger(__name__)

class Diagnostics:

    """
    Set of diagnostics to be run for determining the health of the
    host running Jasper

    To add new checks, add a boolean returning method with a name that starts
    with `check_`
    """

    @classmethod
    def check_network_connection(cls):
        try:
            # see if we can resolve the host name -- tells us if there is
            # a DNS listening
            host = socket.gethostbyname("www.google.com")
            # connect to the host -- tells us if the host is actually
            # reachable
            socket.create_connection((host, 80), 2)
        except Exception:
            return False
        else:
            return True

    @classmethod
    def check_phonetisaurus_dictionary_file(cls):
        return os.path.isfile(os.path.join(jasperpath.APP_PATH, "..", "phonetisaurus/g014b2b.fst"))

    @classmethod
    def check_phonetisaurus_program(cls):
        return cls.do_check_program('phonetisaurus-g2p')

    @classmethod
    def check_espeak_program(cls):
        return cls.do_check_program('espeak')

    @classmethod
    def check_say_program(cls):
        return cls.do_check_program('say')

    @classmethod
    def do_check_program(cls, program):
        return find_executable(program) is not None

    @classmethod
    def check_all_pip_requirements_installed(cls):
        requirements = list(parse_requirements('requirements.txt'))
        packages = [ req.name for req in requirements ]
        installed_packages = [ pkg['name'] for pkg in list(search_packages_info(packages))]
        missing_packages = [ pkg for pkg in packages if pkg not in installed_packages ]
        if missing_packages:
            logger.info("Missing packages: "+', '.join(missing_packages))
            return False
        else:
            return True

    @classmethod
    def info_git_revision(cls):
        return subprocess.check_output(['git', 'rev-parse', 'HEAD'])


class DiagnosticRunner:

    """
    Performs a series of checks against the system, printing the results to the
    console and also saving them to diagnostic.log
    """

    def __init__(self, diagnostics):
        self.diagnostics = diagnostics

    def run(self):
        self.initialize_log()
        self.perform_checks()

    def perform_checks(self):
        self.failed_checks = 0
        for check in self.select_methods('check'):
            self.do_check(check)
        for info in self.select_methods('info'):
            self.get_info(info)
        if self.failed_checks == 0:
            logger.info("All checks passed")
        else:
            logger.info("%d checks failed" % self.failed_checks)

    def select_methods(self, prefix):
        def is_match(method_name):
            return callable(getattr(self.diagnostics, method_name)) and re.match(r"\A" + prefix + "_", method_name)

        return [method_name for method_name in dir(self.diagnostics) if is_match(method_name)]

    def initialize_log(self):
        logger.info("Starting jasper diagnostic at %s" % time.strftime("%c"))

    def get_info(self, info_name):
        message = info_name.replace("info_", "").replace("_", " ")
        info_method = getattr(self.diagnostics, info_name)
        info = info_method()
        logger.info("%s: %s" % (message, info))

    def do_check(self, check_name):
        message = check_name.replace("check_", "").replace("_", " ")
        check = getattr(self.diagnostics, check_name)
        if check():
            result = "OK"
        else:
            self.failed_checks += 1
            result = "FAILED"

        logger.info("Checking %s... %s" % (message, result))


if __name__ == '__main__':
    logging.basicConfig(stream=sys.stdout, level=logging.INFO)

    DiagnosticRunner(Diagnostics).run()


