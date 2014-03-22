Introduction
============


The package allows you to audit actions being done on your site. It accomplishes
this by using configurable content rules.

By default, after you activate this package, it'll create all the content rules
that can be used for auditing with only the Page type to audit OOTB. If you want
to audit more types of objects, you'll need to configure the content rules.

The audits are stored into a relational database.

To configuration the relational database, go to Site Setup, then the
Configuration Registry and search for `collective.auditlog.connectionstring`.
The configuration string needs to be a valid SQLAlchemy connection string.
