## Script (Python) "save_action"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=action='', obj='', count='1', url=''
##title=Save actions to DataWarehouse
##
from collective.auditlog.async import queueJob

queueJob(context, action, obj, count, url)
