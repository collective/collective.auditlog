Changelog
=========

1.4.0a3 (2019-04-10)
--------------------

- Fix soft dependency on formlib (#22)
  [ale-rt]


1.4.0a2 (2018-10-11)
--------------------

- Speed up rule retrieval
  [ale-rt]


1.4.0a1 (2018-08-30)
--------------------

- Deprecate some utility methods.
  [ale-rt]
- Added some memoized properties and methods to the `AuditActionExecutor` class
  for easier customization
  [ale-rt]


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
