from setuptools import setup, find_packages
from marcus import __version__

# install_requires = []
# try:
#     requirements = open('requirements.txt')
#     for line in requirements.readlines():
#         line = line.strip()
#         if line and not line.startswith('#'):
#             install_requires.append(line)
# finally:
#     requirements.close()

long_description = ""
try:
    readme = open("README.rst")
    long_description = str(readme.read())
    readme.close()
except:
    pass

setup(
    name='marcus',
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
    install_requires=['setuptools', ],
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
