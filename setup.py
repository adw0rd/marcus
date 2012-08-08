from setuptools import setup, find_packages

setup(
    name='marcus',
    version="0.1",
    description="Bilingual blog on Django",
    long_description="",
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
        "Programming Language :: Python",
        "Framework :: Django",
        "Environment :: Web Environment",
    ],
)
