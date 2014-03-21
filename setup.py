from setuptools import setup, find_packages
import os

version = '1.0'

setup(name='collective.auditlog',
      version=version,
      description="Provides extra conditions and triggers for all content "
                  "actions",
      long_description="%s\n%s" % (
          open("README.txt").read(),
          open(os.path.join("docs", "HISTORY.txt")).read()),
      # Get more strings from
      # http://pypi.python.org/pypi?:action=list_classifiers
      classifiers=[
          "Framework :: Plone",
          "Programming Language :: Python",
      ],
      keywords='',
      author='',
      author_email='',
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
