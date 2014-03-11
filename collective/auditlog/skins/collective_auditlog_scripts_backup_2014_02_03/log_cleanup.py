## Script (Python) "log_cleanup"
##title=Cleans DataWarehouse Entries
##bind container=container
##bind context=context
##parameters=

##This fixes entries in the Data Warehouse DB that have the initial create id (contenttype.date.millisecs) instead of the proper title/shortname.


def fixEntries(results, createID):
  for entry in results:
    try:
      uid = entry['UID']
      indexes = context.portal_catalog(UID=uid)
      if len(indexes) > 0:
        obj = indexes[0].getObject()
        id = obj.getId()
        title = obj.Title()
        path = '/'.join(obj.getPhysicalPath())
    
        context.dbAddContentAction(ID=id, UID=uid, Action=entry['Action'], Title=title, Path=path, CreateID=createID)
    except:
      pass

def getResults(createID):
        results = context.dbSelectContentAction(CreateID=createID)
        if len(results) > 0:
          fixEntries(results, createID)

try:
  today = DateTime().strftime('%Y-%m-%d')
  yesterday = DateTime(DateTime() - 1).strftime('%Y-%m-%d')
  createID = "%." + today + ".%"
  createID2 = "%." + yesterday + ".%"
  getResults(createID)
  getResults(createID2)
  return "Success"
except:
  return "Failed"

