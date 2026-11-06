from setuptools import setup

version = "4.0.0.dev0"


long_description = "\n\n".join(
    [
        open("README.rst").read(),
        open("CHANGES.rst").read(),
    ]
)


setup(
    name="collective.auditlog",
    version=version,
    description=("Provides extra conditions and triggers for all content " "actions"),
    long_description=long_description,
    # Get more strings from https://pypi.org/classifiers/
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Framework :: Plone",
        "Framework :: Plone :: 6.2",
        "Framework :: Plone :: 6.3",
        "Framework :: Plone :: Addon",
        "Framework :: Zope",
        "Framework :: Zope :: 4",
        "Framework :: Zope :: 5",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3 :: Only",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Programming Language :: Python :: 3.13",
        "Programming Language :: Python :: 3.14",
        "Programming Language :: Python :: 3.15",
        "Operating System :: OS Independent",
    ],
    keywords="Plone Audit Log",
    author="rain2o",
    author_email="Joel@rain2odesigns.com",
    url="https://github.com/collective/collective.auditlog/",
    project_urls={
        "PyPI": "https://pypi.org/project/collective.auditlog/",
        "Source": "https://github.com/collective/collective.auditlog",
        "Tracker": "https://github.com/collective/collective.auditlog/issues",
    },
    license_expression="GPL-2.0-or-later",
    license_files=("docs/LICENSE.txt", "docs/LICENSE.GPL"),
    include_package_data=True,
    zip_safe=False,
    install_requires=[
        "Zope",
        "Products.CMFCore",
        "Products.CMFPlone",
        "Products.PluggableAuthService",
        "Products.ZCatalog",
        "plone.app.registry",
        "plone.base",
        "plone.contentrules",
        "plone.dexterity",
        "plone.memoize",
        "plone.uuid",
        "sqlalchemy",
        "plone.api",
        "plone.app.contentrules",
        "plone.app.discussion",
        "plone.app.iterate",
    ],
    python_requires=">=3.11",
    extras_require={
        "celery": [
            "collective.celery",
        ],
        "test": [
            "plone.app.testing",
            "plone.app.contenttypes",
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
