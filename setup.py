# coding=utf-8
from setuptools import find_packages
from setuptools import setup

import os


version = "2.0.dev0"


long_description = "\n\n".join([open("README.rst").read(), open("CHANGES.rst").read(),])


setup(
    name="collective.auditlog",
    version=version,
    description=("Provides extra conditions and triggers for all content " "actions"),
    long_description=long_description,
    # Get more strings from
    # http://pypi.python.org/pypi?:action=list_classifiers
    classifiers=[
        "Framework :: Plone",
        "Framework :: Plone :: 5.1",
        "Framework :: Plone :: 5.2",
        "Programming Language :: Python",
        "Programming Language :: Python :: 2.7",
        "Operating System :: OS Independent",
    ],
    keywords="Plone Audit Log",
    author="rain2o",
    author_email="Joel@rain2odesigns.com",
    url="http://svn.plone.org/svn/collective/",
    license="GPL",
    packages=find_packages(),
    namespace_packages=["collective"],
    include_package_data=True,
    zip_safe=False,
    install_requires=["setuptools", "sqlalchemy", "plone.app.contentrules",],
    extras_require={
        "celery": ["collective.celery",],
        "test": [
            "plone.app.testing",
            "plone.app.contenttypes",
            "pysqlite;python_version<'3'",
        ],
    },
    entry_points="""
      # -*- Entry points: -*-

      [z3c.autoinclude.plugin]
      target = plone

      [celery_tasks]
      audit = collective.auditlog.tasks
      """,
)
