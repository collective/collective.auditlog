Introduction
============

The package allows you to audit actions being done on your site.
It accomplishes this by using configurable content rules.

By default, after you activate this package,
it'll create all the content rules
that can be used for auditing with only the Page type to audit OOTB.
If you want to audit more types of objects,
you'll need to configure the content rules.

The audits are stored into a relational database.
Once installed and called for the first time
it will create a table called "audit" if it does not already exist,
so there is no need to create the table manually.

AuditLog attempts to use plone.app.async to perform the store actions,
but if that fails it will finish the task directly.
The advantage of this is to allow an individual 'worker' client
to run Async and handle all of these request.
If there is a lot of activity it will not get backed up.
Async queues the job up and handles it as it can
while the users request finishes and moves on
avoiding sacrifices in performance.
Refer to the collective.async pypi page
for instructions on setting it up if you use it.
Async is NOT required for AuditLog to work,
however it is advised, especially for high traffic sites.


Installation
============

Download the package from GitHub and extract into your src directory.
Add 'collective.auditlog' to your eggs and zcml slugs in buildout.
Include the location (src/collective.auditlog) in development slugs too.
Run buildout

In Site Setup -> Add-ons, active Audit Log.
Once it is installed you will see "AuditLog" under Add-on Configuration.
This is where you can configuration the relational database.
The configuration string needs to be a valid SQLAlchemy connection string.
The control panel also allows you to enable/disable
tracking of actions performed on working copies.

All that is left is to configure the new Content Rules
to track the content types and actions you desire.


Dependencies
============

All dependencies are installed automatically
when installing collective.auditlog.
Here is just a list of those for reference:

- setuptools
- sqlalchemy
- five.globalrequest
- plone.app.async


Authors
=======

- Joel Rainwater, initial author
- Nathan van Gheem, Async integration, bug fixes, optimization.
