import os
import unittest

PATTERN = "test_*.py"


def load_tests(loader, tests, pattern):
    # Add core tests (from this package)
    core_tests_dir = os.path.dirname(os.path.abspath(__file__))
    tests.addTests(loader.discover(core_tests_dir, PATTERN))

    # Add plugin tests
    plugin_dir = os.path.abspath(os.path.join(
        core_tests_dir, os.path.pardir, "plugins"))
    for name in os.listdir(plugin_dir):
        path = os.path.join(plugin_dir, name)
        if os.path.isdir(path):
            plugin_loader = unittest.TestLoader()
            plugin_tests = plugin_loader.discover(path, "test_*.py", path)
            tests.addTests(plugin_tests)

    return tests
