Changelog
=========

1.4 (unreleased)
----------------

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
