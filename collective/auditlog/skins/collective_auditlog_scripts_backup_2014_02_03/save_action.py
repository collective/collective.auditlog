## Script (Python) "save_action"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=action='', obj='', count='1', url=''
##title=Save actions to DataWarehouse
##
from collective.auditlog.functionality import AuditLogTest, AuditLogChecker


request = container.REQUEST

audit_tool = AuditLogChecker()
action = audit_tool.checkAction(action, context, request)
if not action:
  return
webFormFields = ['Readonly String Field', 'Thanks Page', 'Text Field', 'String Field', 'Selection Field', 'Save Data Adapter', 'RichText Field', 'Rich Label Field', 'Password Field', 
                 'Multi-Select Field', 'Mailer Adapter', 'Lines Field', 'Rating-Scale Field', 'Label Field', 'Whole Number Field', 'Decimal Number Field', 'File Field', 'Date/Time Field', 
                 'Custom Script Adapter', 'Captcha Field', 'Checkbox Field', 'Fieldset Folder']
info = {}
info['adid'] = context.getCurrentUserName()
info['dt'] = DateTime().strftime('%Y-%m-%d %X')
info['time'] = DateTime().Time()
info['copyOf'] = False
info['action'] = action
info['count'] = count
info['field'] = ''
info['temp'] = ''
sitename = context.absolute_url().split('//')[1].split('.')
info['cancel'] = False
if len(sitename) > 1:
  if sitename[0] == 'www':
    info['sitename'] = sitename[1]
  else:
    info['sitename'] = sitename[0]
elif len(sitename) >= 0:
  info['sitename'] = sitename[0]
else:
  info['sitename'] = ''
info['createID'] = context.portal_type.lower() + ".%"
sep = '/'
co = "copy_of_"
fields = ['url', 'title', 'type', 'id', 'uid', 'count']
if obj=='':
  obj = context
if url:
  if "?" in url:
      path = url.split('?')
      url = path[0]
  path = url.split('/')
  del path[:3]
  last = len(path)-1
  if 'view' in path[last] or 'folder_contents' in path[last]:
    del path[last]
  path.insert(0, '')
  path.insert(1, context.getPhysicalPath()[1])
  id = path[len(path)-1]
  del path[len(path)-1]
  path = '/'.join(path)
  indexes = context.portal_catalog(path=path, id=id)
  obj = indexes[0].getObject()

def takeAction(info):
 if not info['cancel']:
  if 'copy_of_' in info['id']:
    info['id'] = info['id'].replace('copy_of_', '')

  if 'copy_of_' in info['url']:
    info['url'] = info['url'].replace('copy_of_', '')
    info['copyOf'] = True

  cp = context.dbSelectContentAction(Action='checkout', TempUID=info['uid'])
  if len(cp)>0:
    info['temp'] = info['uid']
    info['uid'] = cp[0]['UID']

  try:
    context.dbAddContentAction(ADID=info['adid'], Date=info['dt'], ID=info['id'], UID=info['uid'], Temp=info['temp'], Type=info['type'], Title=info['title'], 
                               Path=info['url'], SiteName=info['sitename'], Action=info['action'], Field=info['field'], CopyOf=info['copyOf'], Count=info['count'], 
                               CreateID=info['createID'])
  except:
    return "Failed"
 else:
  return
def getObjInfo(obj):
  try:
    info['url'] = sep.join(obj.getPhysicalPath())
  except:
    info['url'] = sep.join(context.getPhysicalPath())
  info['title'] = obj.Title()
  info['type'] = obj.Type()
  info['id'] = obj.getId()
  info['uid'] = obj.UID()
  info['pt'] = obj.portal_type

def checkIsForm(obj):
  n = len(context.getPhysicalPath())
  info['field'] = obj.getId()
  while n>0:
   try:
    info['url'] = str(info['url']).replace('/'+info['id'], '')
    id = info['url'].split('/')[len(info['url'].split('/'))-1]
    indexes = context.portal_catalog(path=info['url'], id=id)
    obj = indexes[0].getObject()
    info['type'] = obj.Type()
    info['title'] = obj.Title()
    info['id'] = obj.getId()
    info['uid'] = obj.UID()
    if "Web Form" in info['type']:
      if "field_" not in info['action']:
        info['action'] = "field_%s" % info['action']
      n = 0
      break
    else:
      n -= 1
   except:
     info['cancel'] = True
     break

def checkIsFolder():
  contained = context.portal_catalog.searchResults(dict(path=info['url']))
  if len(contained) > 1:
    for item in contained:
      obj = item.getObject()
      getObjInfo(obj)
      if info['type'] in webFormFields:
        if "added" in info['action']:
          checkIsForm(obj)
        else:
          continue
      else:
        info['field'] = ''
        info['action'] = info['action'].replace('field_', '')
      takeAction(info)
    return False
  else:
    return True

if 'field_' in action:
  info['id'] = obj.getId()
  info['url'] = sep.join(obj.getPhysicalPath())
  if ("form.%s" % info['dt']) not in info['url']:
    checkIsForm(obj)
    takeAction(info)

elif obj and action!='delete':
  actionNeeded = True
  getObjInfo(obj)
  if action=="checkout":
    path = info['url'].replace('/'+info['id'], '')
    ind = context.portal_catalog(path=path)
    for brain in ind:
      obj = brain.getObject()
      if info['id'] in obj.getId() and info['id']!=obj.getId():
        info['temp'] = obj.UID()
        t = DateTime()-.001
        sdate = DateTime(t).strftime('%Y-%m-%d %X')
        cp = context.dbSelectContentAction(Action="added", UID=info['temp'], SDate=sdate, EDate=info['dt'])
        if len(cp) > 0:
          break
  if action=='workflow':
    info['action'] = context.portal_workflow.getInfoFor(context, 'action')
  if action=='added' or action=='move':
    actionNeeded = checkIsFolder()
  if actionNeeded:
    takeAction(info)

elif action=='delete':
  try:
    for item in obj:
      if item['failed']:
        for field in fields:
          info[field] = item['url']
        info['action'] = 'failed'
      else:
        for field in fields:
          info[field] = item[field]
      confirmed = context.dbSelectContentAction(UID=info['uid'], Action="confirmed_delete")
      if len(confirmed)>0:
        continue
      if item['pt'][:4] == "Form" or item['pt']=="FieldsetFolder":
        n = len(item['url'].split('/'))
        info['field'] = info['id']
        id = info['id']
        while n > 0:
          info['url'] = info['url'].replace('/'+id, '')
          id = info['url'].split('/')[len(info['url'].split('/'))-1]
          url = info['url'].replace('/'+id, '')
          indexes = context.portal_catalog(path=url, id=id)
          for index in indexes:
            f_obj = index.getObject()
            info['type'] = f_obj.Type()
            info['id'] = f_obj.getId()
            if "WebForm" in info['type'] or "Web Form" in info['type']:
              info['action'] = "field_delete"
              info['title'] = f_obj.Title()
              info['uid'] = f_obj.UID()
              break
          if "Web Form" in info['type']:
            break
          else:
            n -= 1
      exists = len(context.dbSelectContentAction(UID=info['uid'], Action='delete')) > 0
      if not exists:
        takeAction(info)
  except:
    getObjInfo(obj)
    confirmed = context.dbSelectContentAction(UID=info['uid'], Action="confirmed_delete")
    if len(confirmed)<=0:
      if info['pt'][:4] == "Form" or info['pt'] == "FieldsetFolder":
        checkIsForm(obj)
      takeAction(info)

elif action=="update_suggested":
  getObjInfo(obj)
  takeAction(info)

else:
  request = context.REQUEST
  form = request.form
  info['url'] = sep.join(context.getPhysicalPath())
  info['uid'] = context.UID()

  try:
    indexes = context.portal_catalog(UID=info['uid'])
    obj = indexes[0].getObject()
    info['id'] = obj.getId()
    info['type'] = obj.Type()
    info['title'] = obj.Title()
  except:
    info['id'] = form['title'].replace(' ', '-').replace('/', '-').lower()
    info['title'] = form['title']
    info['action'] = 'Add New'
    info['path'] = context.getPhysicalPath()
    info['type'] = 'Error'
    if 'portal_factory' in info['path']:
      for i, elem in enumerate(info['path']):
        if elem == 'portal_factory':
          info['type'] = contentTypes[info['path[(i+1)]']]

  takeAction(info)

#def store_action(action, context, request):
#	  context.auditLog(action, context, request)

#request = container.REQUEST
#store_action(action, context, request)
#context.pySaveContentAction(action, context)
