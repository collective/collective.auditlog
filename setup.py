# coding=utf-8
from setuptools import find_packages
from setuptools import setup
import os

version = '1.2.1'

setup(
    name='collective.auditlog',
    version=version,
    description=(
        "Provides extra conditions and triggers for all content "
        "actions"
    ),
    long_description="%s\n%s" % (
        open("README.rst").read(),
        open(os.path.join("docs", "HISTORY.rst")).read(),
    ),
    # Get more strings from
    # http://pypi.python.org/pypi?:action=list_classifiers
    classifiers=[
        "Framework :: Plone",
        "Framework :: Plone :: 4.3",
        "Framework :: Plone :: 5.0",
        "Programming Language :: Python",
        "Programming Language :: Python :: 2.7",
        "Operating System :: OS Independent"
    ],
    keywords='Plone Audit Log',
    author='rain2o',
    author_email='Joel@rain2odesigns.com',
    url='http://svn.plone.org/svn/collective/',
    license='GPL',
    packages=find_packages(exclude=['ez_setup']),
    namespace_packages=['collective'],
    include_package_data=True,
    zip_safe=False,
    install_requires=[
        'setuptools',
        'sqlalchemy',
        'five.globalrequest'
    ],
    extras_require={
        'async': [
            'plone.app.async',
        ]
    },
    entry_points="""
      # -*- Entry points: -*-

      [z3c.autoinclude.plugin]
      target = plone
      """
)
