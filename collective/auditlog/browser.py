from collective.auditlog import db
from collective.auditlog.models import LogEntry
from Products.Five.browser import BrowserView
from sqlalchemy import desc
from sqlalchemy import or_


class LogView(BrowserView):

    page_size = 100

    columns = [
        {"name": "user", "label": "User"},
        {"name": "performed_on", "label": "Date"},
        {"name": "uid", "label": "UID"},
        {"name": "type", "label": "Type"},
        {"name": "title", "label": "Title"},
        {"name": "path", "label": "Path"},
        {"name": "site_name", "label": "Site"},
        {"name": "working_copy", "label": "Working Copy"},
        {"name": "action", "label": "Action"},
        {"name": "info", "label": "Notes"},
    ]

    @property
    def page(self):
        page = self.request.get("page", "1")
        page = int(page)
        return page

    @property
    def direction(self):
        dir = self.request.get("direction", "asc")
        return dir

    def new_direction(self, order, column):
        new = "asc"
        if order == column and self.direction == "asc":
            new = "desc"
        return new

    @property
    def pagination_next(self):
        url = self.request.URL
        if self.request.QUERY_STRING:
            url = url + "?" + self.request.QUERY_STRING
            url = url.replace("page=", "page=" + str(self.page + 1) + "&prev=")
            if "page" not in url:
                url = url + "&page=2"
        else:
            url = url + "?page=" + str(self.page + 1)
        return url

    @property
    def loglines(self):
        order = self.request.get("order", "performed_on")
        query = self.request.get("query", "")
        session = db.getSession()
        if self.direction == "asc":
            lines = session.query(LogEntry).order_by(order)
        else:
            lines = session.query(LogEntry).order_by(desc(order))
        if query:
            query = unicode(query)
            lines = lines.filter(
                or_(
                    LogEntry.user.contains(query),
                    LogEntry.uid.contains(query),
                    LogEntry.type.contains(query),
                    LogEntry.title.contains(query),
                    LogEntry.path.contains(query),
                    LogEntry.site_name.contains(query),
                    LogEntry.working_copy.contains(query),
                    LogEntry.action.contains(query),
                    LogEntry.info.contains(query),
                )
            )
        lines = lines.limit(self.page_size)
        lines = lines.offset((self.page - 1) * self.page_size)
        return lines.all()
