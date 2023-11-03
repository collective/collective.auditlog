3.0.0a2 (2023-11-03)
--------------------

Breaking changes:


- Complete the removal of Archetypes code: ``is_portal_factory`` and ``WorkingCopyRelation`` are gone for good.
  [ale-rt] (#33)


3.0.0a1 (2023-06-01)
--------------------

Internal:


- Update configuration files.
  [plone devs] (53dc5b4c)


3.0.0a1 (unreleased)
--------------------

- Drop Python 2.7
- Use SQLAlchemy 1.4
  [ale-rt]

2.0.0 (2023-05-31)
------------------

- Re-release 2.0.0a2 as 2.0.0.
  This will be the last release supporting Python2.7.
  [ale-rt]


2.0.0a2 (2020-03-19)
--------------------

- Fix request not having an environment attribute in instance scripts
  [ale-rt]


2.0.0a1 (2020-03-11)
--------------------

- Remove inconsistent passing of ``request`` parameter and use zope.globalrequest instead.
  [thet]

- Remove deprecations.
  action.canExecute is renamed to ``can_execute``, takes no parameters and is a property.
  [thet]

- Python 3 compatibility.
  [thet]

- Remove support for plone.app.async.
  Due to  ``async`` being a reserved word, this cannot made Python 3 compatible.
  Use collective.celeries instead.
  [thet]

- Drop support for Archetypes.
  [thet]

- Plone 5.2 compatibility.
  Drop Support for Plone 5.0 and 4.3 (Both are missing zope.interface.interfaces.IObjectEvent).
  [thet]

- Make Arhcetype a soft dependency.
  [ale-rt]

- Align with Plone code style: black, isort.
  [thet]

- Fix soft dependency on formlib (#22)
  [ale-rt]

- Speed up rule retrieval
  [ale-rt]

- Added some memoized properties and methods to the `AuditActionExecutor` class
  for easier customization
  [ale-rt]

- collective.celery integration
  [enfold]

- @@auditlog-view allows viewing/sorting/searching audit log entries
  [enfold]

- add login & logout audits
  [enfold]

- ability to specify the sqlalchemy DSN in config file
  [enfold]

- Notify an event before storing audit log entry.
  [enfold]

- Use custom permission for viewing audit log.
  [enfold]

- Fix tests.
  [enfold]

- Fix db connection leak.
  [enfold]

- Use valid json in info field.
  [enfold]


1.3.3 (2018-07-12)
------------------

- Factored out getObjectInfo and addLogEntry.
  [reinhardt]


1.3.2 (2018-07-11)
------------------

- Skip retrieving rule when audit log is disabled completely.
  Improves performance.
  [reinhardt]


1.3.1 (2017-04-13)
------------------

- Fix upgrade step title.
  [ale-rt]


1.3.0 (2017-04-13)
------------------

- The engine parameters (like pool_recycle, echo, ...)
  can be specified through a registry record
  [ale-rt]


1.2.2 (2016-06-06)
------------------

- Make action more robust on IActionSucceededEvent
  [ale-rt]


1.2.1 (2016-05-10)
------------------

- Fix unicode issues
- Tests are working again
  [ale-rt]


1.2.0 (2016-05-03)
------------------

- First public release
