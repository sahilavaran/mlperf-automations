# Build a whl file for mlperf-automations

from setuptools import setup
from setuptools._distutils.dist import Distribution
from setuptools.command.install import install
import subprocess
import sys
import importlib.util
import platform
import os
import shutil

# Try to use importlib.metadata for Python 3.8+
try:
    if sys.version_info >= (3, 8):
        from importlib.metadata import version, PackageNotFoundError
    else:
        # Fallback to pkg_resources for Python < 3.8
        import pkg_resources
        PackageNotFoundError = pkg_resources.DistributionNotFound
except ImportError:
    # If importlib.metadata is unavailable, fall back to pkg_resources
    import pkg_resources
    PackageNotFoundError = pkg_resources.DistributionNotFound


class CustomInstallCommand(install):
    def run(self):
        self.get_sys_platform()
        self.install_system_packages()

        # Call the standard run method
        install.run(self)

        # Call the custom function
        return self.custom_function()

    def is_package_installed(self, package_name):
        try:
            if sys.version_info >= (3, 8):
                spec = importlib.util.find_spec(package_name)
                module = importlib.util.module_from_spec(spec)
                sys.modules[package_name] = module
                spec.loader.exec_module(module)
            else:
                pkg_resources.get_distribution(
                    package_name)  # Fallback for < 3.8
            return True
        except PackageNotFoundError:
            return False

    def install_system_packages(self):
        # List of packages to install via system package manager
        packages = []

        git_status = self.command_exists('git')
        if not git_status:
            packages.append("git")
        wget_status = self.command_exists('wget')
        if not wget_status:
            packages.append("wget")
        curl_status = self.command_exists('curl')
        if not curl_status:
            packages.append("curl")

        name = 'venv'

        if name in sys.modules:
            pass  # nothing needed
        elif self.is_package_installed(name):
            pass
        else:
            packages.append("python3-venv")

        if packages:
            if self.system == 'Linux' or self.system == 'Darwin':
                manager, details = self.get_package_manager_details()
                if manager:
                    if manager == "apt-get":
                        # Check if 'sudo' is available
                        if shutil.which('sudo'):
                            subprocess.check_call(
                                ['sudo', 'apt-get', 'update'])
                            subprocess.check_call(
                                ['sudo', 'apt-get', 'install', '-y'] + packages)
                        else:
                            print("sudo not found, trying without sudo.")
                            try:
                                subprocess.check_call(['apt-get', 'update'])
                                subprocess.check_call(
                                    ['apt-get', 'install', '-y'] + packages)
                            except subprocess.CalledProcessError:
                                print(
                                    f"Installation of {packages} without sudo failed. Please install these packages manually to continue!")
            elif self.system == 'Windows':
                print(
                    f"Please install the following packages manually: {packages}")

    def detect_package_manager(self):
        package_managers = {
            'apt-get': '/usr/bin/apt-get',
            'yum': '/usr/bin/yum',
            'dnf': '/usr/bin/dnf',
            'pacman': '/usr/bin/pacman',
            'zypper': '/usr/bin/zypper',
            'brew': '/usr/local/bin/brew'
        }

        for name, path in package_managers.items():
            if os.path.exists(path):
                return name

        return None

    def get_package_manager_details(self):
        manager = self.detect_package_manager()
        if manager:
            try:
                version_output = subprocess.check_output(
                    [manager, '--version'], stderr=subprocess.STDOUT).decode('utf-8')
                return manager, version_output.split('\n')[0]
            except subprocess.CalledProcessError:
                return manager, 'Version information not available'
        else:
            return None, 'No supported package manager found'

    # Checks if command exists(for installing required packages).
    # If the command exists, which returns 0, making the function return True.
    # If the command does not exist, which returns a non-zero value, making the function return False.
    # NOTE: The standard output and standard error streams are redirected to
    # PIPES so that it could be captured in future if needed.
    def command_exists(self, command):
        if self.system == "Linux" or self.system == 'Darwin':
            return subprocess.call(
                ['which', command], stdout=subprocess.PIPE, stderr=subprocess.PIPE) == 0
        elif self.system == "Windows":
            return subprocess.call(
                [command, '--version'], stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True) == 0

    def custom_function(self):
        commit_hash = get_commit_hash()
        import cmind
        clean_mlops_repo = os.environ.get('CM_MLOPS_CLEAN_REPO', 'false')
        if str(clean_mlops_repo).lower() not in ["no", "0", "false", "off"]:
            r = cmind.access({'action': 'rm',
                              'automation': 'repo',
                              'artifact': 'mlcommons@cm4mlops',
                              'force': True,
                              'all': True})

        branch = os.environ.get('CM_MLOPS_REPO_BRANCH', 'dev')
        pull_default_mlops_repo = os.environ.get(
            'CM_PULL_DEFAULT_MLOPS_REPO', 'true')

        if str(pull_default_mlops_repo).lower() not in [
                "no", "0", "false", "off"]:
            r = cmind.access({'action': 'pull',
                              'automation': 'repo',
                              'artifact': 'mlcommons@mlperf-automations',
                              'checkout': commit_hash,
                              'branch': branch})
            print(r)
            if r['return'] > 0:
                return r['return']

    def get_sys_platform(self):
        self.system = platform.system()

# Read long description and version


def read_file(file_name, default=""):
    if os.path.isfile(file_name):
        with open(file_name, "r") as f:
            return f.read().strip()
    return default


def get_commit_hash():
    try:
        with open(os.path.join(os.path.dirname(__file__), 'git_commit_hash.txt'), 'r') as f:
            return f.read().strip()
    except FileNotFoundError:
        return "unknown"


long_description = read_file("README.md", "No description available.")
version_ = read_file("VERSION", "0.3.1")

setup(
    name='cm4mlops',
    version=version_,
    long_description=long_description,
    long_description_content_type='text/markdown',
    url="https://github.com/mlcommons/cm4mlops",
    packages=[],
    install_requires=[
        "setuptools>=60",
        "wheel",
        "cmind",
        "giturlparse",
        "requests",
        "tabulate",
        "pyyaml"
    ],
    cmdclass={
        'install': CustomInstallCommand,
    },
)
