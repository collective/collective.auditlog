from zope.component import getUtility
#from plone.app.async.interfaces import IAsyncService
#import zc.async.dispatcher
from plone.app.layout.viewlets.content import ContentHistoryViewlet
from zope.component import getMultiAdapter


class AuditLogChecker():

    def checkAction(self, action, context, request):

        if action=="added":
          type = context.Type()
          if "Web Form" in type and context.portal_type.lower() in context.absolute_url():
            return False
        if action=="rename" and "Web Form" in context.Type():
	  tools = getMultiAdapter((context, request), name=u'plone_tools')
	  portal_url = tools.url()
          chv = ContentHistoryViewlet(context, request, None, None)
          chv.navigation_root_url = chv.site_url = portal_url()
          history = chv.fullHistory()
          last = history[0]
          comments = last['comments']
          trans = last['transition_title']
          uid = context.UID()
          indexes = context.dbSelectContentAction(UID=uid)
          if (comments == 'Initial revision' or 'Create' in trans) and len(indexes) == 0 and len(history) <=2:
            action = "added"
	return action

#       context.pySaveContentAction(action, context)
#       async = getUtility(IAsyncService)
#       return async
#       print zc.async.dispatcher.get()
#       queue = async.getQueues()['']
#       print queue
#       return printed

class AuditLogTest():

	def testingActions(self):
		print "Test successfull"
		return "Test successfull"

