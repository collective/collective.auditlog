## Script (Python) "log_cleanup"
##title=Cleans DataWarehouse Entries
##bind container=container
##bind context=context
##parameters=


#This fixes entries in the Data Warehouse DB that have the initial create id (contenttype.date.millisecs)
#or the field name is "field_uid: {UID}" instead of the proper title/shortname.
def fixEntries(results, createID):
  for entry in results:
   if 'field_uid: ' in entry['Field']:
    try:
      uid = entry['Field'].replace('field_uid: ', '')
      indexes = context.portal_catalog(UID=uid)
      if len(indexes) > 0:
        obj = indexes[0].getObject()
        title = obj.Title()
        context.dbAddContentAction(ID=entry['ID'], Field=title)
      else:
        moveErrors(entry, True)
    except:
      pass
   else:
    try:
      uid = entry['UID']
      indexes = context.portal_catalog(UID=uid)
      if len(indexes) > 0:
        obj = indexes[0].getObject()
        id = obj.getId()
        title = obj.Title()
        path = '/'.join(obj.getPhysicalPath())
        context.dbAddContentAction(ID=id, UID=uid, Action=entry['Action'], Title=title, Path=path, CreateID=createID)
      else:
	moveErrors(entry, False)
    except:
      pass


#Get all items in DB that have create ID for Content_ID or Field
def getResults(createID):
        results = context.dbSelectContentAction(CreateID=createID, Site=site)
        if len(results) > 0:
          fixEntries(results, createID)

#Gets all entries in DB with blank Title, and replaces with Title from portal_catalog. 
def fixBlanks():
  results = context.dbSelectContentAction(BlankTitle=True, Site=site)
  if len(results) > 0:
    for entry in results:
      try:
        indexes = context.portal_catalog(UID=entry['UID'])
        if len(indexes) > 0:
          obj = indexes[0].getObject()
          title = obj.Title()
          context.dbAddContentAction(ID=entry['ID'], Title=title)
        else:
          moveErrors(entry, False)
      except:
        pass

#Any entry from functions above not found in portal_catalog, it searches DB for a delete action.
#If no delete action, moves to another table called error_log for tracking, and deletes from main table. 
def moveErrors(entry, fieldID):
  if fieldID:
    deleted = (len(context.dbSelectContentAction(Action='field_deleted', Field=entry['Field']))>0)
  else:
    deleted = (len(context.dbSelectContentAction(Action='delete', UID=entry['UID']))>0)

  if not deleted:
      context.dbAddContentAction(ADID=entry['ADID'], Date=entry['Date'], ID=entry['Content_ID'], UID=entry['UID'], Temp=entry['Temp_UID'], Type=entry['Content_Type'], 
                             Title=entry['Title'], Path=entry['Path'], SiteName=entry['Site_Name'], Action=entry['Action'], Field=entry['Field'], 
                             CopyOf=entry['Copy'], Count=entry['Affected_Count'], Error=True)


try:
  site = str(context.absolute_url()).split('/')
  site = site[len(site)-1].split('.')[0]
  today = DateTime().strftime('%Y-%m-%d')
  yesterday = DateTime(DateTime() - 1).strftime('%Y-%m-%d')
  createID = "%." + today + ".%"
  createID2 = "%." + yesterday + ".%"
  getResults(createID)
  getResults(createID2)
  fixBlanks()
  return "Success"
except:
  return "Failed"
