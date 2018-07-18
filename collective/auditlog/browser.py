from Products.Five.browser import BrowserView
from collective.auditlog import db
from collective.auditlog.models import LogEntry
from sqlalchemy import or_


class LogView(BrowserView):

    page_size = 100

    @property
    def page(self):
        page = self.request.get('page', '1')
        page = int(page)
        return page

    @property
    def pagination_next(self):
        url = self.request.URL
        if self.request.QUERY_STRING:
            url = url + '?' + self.request.QUERY_STRING
            url = url.replace('page=', 'page=' + str(self.page + 1) + 'prev=')
        else:
            url = url + "?page=" + str(self.page + 1)
        return url

    @property
    def loglines(self):
        order = self.request.get('order', 'performed_on')
        query = self.request.get('query', '')
        session = db.getSession()
        lines = session.query(LogEntry).order_by(order)
        if query:
            query = unicode(query)
            lines = lines.filter(or_(LogEntry.user.contains(query),
                                     LogEntry.uid.contains(query),
                                     LogEntry.type.contains(query),
                                     LogEntry.title.contains(query),
                                     LogEntry.path.contains(query),
                                     LogEntry.site_name.contains(query),
                                     LogEntry.action.contains(query),
                                     LogEntry.info.contains(query))
                                 )
        lines = lines.limit(self.page_size)
        lines = lines.offset((self.page - 1) * self.page_size)
        return lines.all()
