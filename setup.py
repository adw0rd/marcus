import re
from setuptools import setup, find_packages
from marcus import __version__

# INSTALLATION A PACKAGES FROM requirements.txt
requirements = open('requirements.txt')
install_requires = []
dependency_links = []
try:
    for line in requirements.readlines():
        line = line.strip()
        if line and not line.startswith('#'):  # for inline  comments
            if "#egg" in line:
                names = re.findall('#egg=([^-]+)-', line)
                install_requires.append(names[0])
                dependency_links.append(line)
            else:
                install_requires.append(line)
finally:
    requirements.close()

# LONG DESCRIPTION
long_description = ""
try:
    readme = open("README.rst")
    long_description = str(readme.read())
    readme.close()
except:
    pass

# SETUP
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
)
