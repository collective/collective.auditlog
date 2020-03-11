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

AuditLog attempts to use plone.app.async or collective.celery to
perform the store actions, but if that fails it will finish the task
directly. The advantage of this is to allow an individual 'worker'
client to run Async and handle all of these request.
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

Upgrading
=========

If you are upgrading from an older version, you will need to run the
upgrade steps from the add-ons control panel.

USAGE
=====
For now, collective.auditlog uses SQLAlchemy for storing data. To use
postgres, it's necessary to add the 'psycopg2' egg to the buildout. Once
the product is installed, add the correct connection URL to the product
setup. Example:

postgresql://enfold:enfold@localhost/auditlog

By default, collective.auditlog uses content rules to define which events
to capture. An additional mechanism has been added that allows the site to
automatically log the various events supported by collective.auditlog.
Simply choose from the picklist in the config for this to work. If no
events are selected, no logging will occur.

It is possible to log custom events from application code by using the
AuditableActionPerformedEvent, like this:

from zope event import notify
from collective.auditlog.interfaces import AuditableActionPerformedEvent
notify(AuditableActionPerformedEvent(obj, request, "action", "note"))

'obj', refers to the affected content object; 'request' is the current zope
request, 'action' and 'note' correspond to the logged action and its
description, respectively. All parameters are required, but everything
except obj can be set to None if no value is available.

In addition to control panel configuration, connection parameters can be
set using the zope-conf-additional directive in the buildout. Note that
this will take precedence over any control panel configuration. Example::

    zope-conf-additional =
        <product-config collective.auditlog>
            audit-connection-string postgres://enfold:enfold@localhost/auditlog
            audit-connection-params {"pool_recycle": 3600, "echo": true}
        </product-config>

There is now a view for the audit log entries, located at @@auditlog-view.
There is no link to it from the control panel at the moment. The view uses
infinite scrollong rather than pagination for looking at the logs.

Searching the audit log
=======================

Audit logs are stored in a SQL table, so you can use any SQL database tool
to analyse the audit log. However, sometimes you may need to query the logs
in the context of the Plone objects that generated them, for which the
information stored in SQL is not enough. For this purpose,
collective.auditlog offers a catalog based mechanism which can be used to
query the logs using any Plone based indexes available at the time of
logging. This can be used, for example, to develop a portlet that shows the
latest documents that have been modified.

To enable catalog-based logging, choose sql+zodb storage in the audit log
control panel. Information will still be stored in the SQL database, but
a special catalog will be enabled to store plone indexing information as
well.

Once this storage is enabled, you can search the logs using a catalog-like
query::

    from datetime import datetime
    from collective.auditlog.catalog import searchAudited

    from = datatime(2018,6,1)
    to = datetime(2018,12,31)
    query = {'portal_type': 'Document',
            'review_state': 'published'}
    audited = searchAudited(from_date=from,
                            to_date=to,
                            actions=['added', 'modified'],
                            **query)

All of the parameters are optional, but an empty query will return all
indexed objects, so use with care.

Note that the query will return catalog records, and any documents that have
multiple actions performed in the selected date range, will only appear once
in the list. There are also catalog records for deleted items, so a query
can be made to look for those even if they are gone from Plone.


Celery Integration
==================
The collective.celery package requires adding the celery and
collective.celery eggs to the mian buildout section eggs. Example:

eggs =
    celery
    Plone
    collective.celery

We still use the celery-broker part, for clarity. The celery part is
still required, but is simpler::

    [celery-broker]
    host = 127.0.0.1
    port = 6379

    [celery]
    recipe = zc.recipe.egg
    environment-vars = ${buildout:environment-vars}
    eggs =
        ${buildout:eggs}
        flower
    scripts = pcelery flower

The celery part depends on having some variables added to the main
environment-vars section::

    environment-vars =
        CELERY_BROKER_URL redis://${celery-broker:host}:${celery-broker:port}
        CELERY_RESULT_BACKEND redis://${celery-broker:host}:${celery-broker:port}
        CELERY_TASKS collective.es.index.tasks

Additional Zope configuration
-----------------------------

There's now a hook in collective.celery for carrying out additional zope
configuration before running the tasks. If the tasks module contains an
'extra_config' method, it is passed the zope startup object at worker
initialization time. This is used by collective.es.index to run the
elasticsearch configuration method.

Monitoring celery tasks
-----------------------

Celery needs to be started as an independent process. It's recommended to
use supervisord for this. To try it out from the command line, you can run
"bin/pcelery worker" from the buildout directory. Note that the script is
now named 'pcelery' and it needs a path to the zope configuration. Example:

$ bin/pcelery worker parts/client1/etc/zope.conf

Flower is included in this setup. Run "bin/flower" from the buildout
directory and consult the dashboard at http://localhost:5555 using a
browser. Note that the broker is now a requried parameter:

$ bin/flower --broker redis://127.0.0.1:6379

Dependencies
============

All dependencies are installed automatically
when installing collective.auditlog.
Here is just a list of those for reference:

- setuptools
- sqlalchemy
- five.globalrequest
- plone.app.async [OPTIONAL]
- collective.celery [OPTIONAL]

Authors
=======

- Joel Rainwater, initial author
- Nathan van Gheem, Async integration, bug fixes, optimization.
- Alessandro Pisa, bug fixing, testing
- Enfold Systems, celery integration and audit view
