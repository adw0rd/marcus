import re
import os
import sys

from setuptools import setup, find_packages
from setuptools.command.install_lib import install_lib as _install_lib
from distutils.command.build import build as _build
from distutils.cmd import Command

from marcus import __version__


class compile_translations(Command):
    description = 'compile message catalogs to MO files via django compilemessages'
    user_options = []

    def initialize_options(self):
        pass

    def finalize_options(self):
        pass

    def run(self):
        from django.core.management.commands.compilemessages import Command as CompileMessages

        curdir = os.getcwd()
        os.chdir(os.path.join(os.path.dirname(__file__), 'marcus'))
        cmd = CompileMessages()
        cmd.stdout = sys.stdout
        cmd.stderr = sys.stderr
        cmd.handle(verbosity=4)
        os.chdir(curdir)


class build(_build):
    sub_commands = [('compile_translations', None)] + _build.sub_commands


class install_lib(_install_lib):

    def run(self):
        self.run_command('compile_translations')
        _install_lib.run(self)


# Installation a packages from "requirements.txt"
requirements = open('requirements.txt')
install_requires = []
dependency_links = []
setup_requires = []
try:
    for line in requirements.readlines():
        line = line.strip()
        if line and not line.startswith('#'):  # for inline comments
            if "#egg" in line:
                names = re.findall('#egg=([^-]+)-?', line)
                install_requires.append(names[0])
                links = [link for link in line.split() if '://' in link]
                dependency_links.append(links[0])
            else:
                install_requires.append(line)
                if "Django" in line:
                    setup_requires.append(line)
finally:
    requirements.close()

# Getting long_description
long_description = ""
try:
    readme = open("README.rst")
    long_description = str(readme.read())
    readme.close()
except:
    pass

setup(
    name='django-marcus',
    version=__version__,
    description="Bilingual blog on Django",
    long_description=long_description,
    keywords='django, blog',
    author='Mikhail Andreev',
    author_email='x11org@gmail.com',
    url='http://github.com/adw0rd/marcus',
    license='BSD',
    packages=find_packages(),
    zip_safe=False,
    install_requires=install_requires,
    dependency_links=dependency_links,
    setup_requires=setup_requires,
    package_data={'': ['requirements.txt']},
    include_package_data=True,
    classifiers=[
        "Environment :: Web Environment",
        "Programming Language :: Python",
        "Framework :: Django",
        "License :: OSI Approved :: BSD License",
        "Topic :: Software Development :: Debuggers",
        "Topic :: Software Development :: Libraries :: Application Frameworks",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
    cmdclass={
        'build': build,
        'install_lib': install_lib,
        'compile_translations': compile_translations
    }
)
