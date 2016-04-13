import os
import tornado.gen
import tornado.httpserver
import tornado.ioloop
import tornado.web
import tornado_mysql

from tornado.options import define, options
define("port", default=8888, help="run on the given port", type=int)

import dbhelper
from base_handler import BaseHandler
from group import GroupNewHandler, GroupOwnHandler, GroupUpdateHandler, GroupDeleteHandler
from category import CategoryHandler, CategoryNewHandler, CategoryUpdateHandler, CategoryDeleteHandler

class MainHandler(BaseHandler):
    @tornado.gen.coroutine
    def get(self):        
        cur = yield self.db.execute("select groups.id, groups.name, category.name, groups.description, groups.created_by, groups.timestamp from groups left join category on groups.category_id=category.id")
        grouplist = []
        for row in cur:
            dict = {'id':str(row[0]), 'name':row[1], 'category_id':str(row[2]), 'description':str(row[3]), 'created_by':str(row[4]), 'created_date':str(row[5])}
            grouplist.append(dict)
        cur.close()
        self.render("index.html", groups=grouplist)
           
class Application(tornado.web.Application):
    def __init__(self):
        handlers = [(r"/", MainHandler),
            (r"/group", MainHandler),
            (r"/group/own/([^/]+)", GroupOwnHandler),
            (r"/group/new", GroupNewHandler),
            (r"/group/update/([^/]+)", GroupUpdateHandler),
            (r"/group/delete/([^/]+)", GroupDeleteHandler),
            (r"/category", CategoryHandler),
            (r"/category/new", CategoryNewHandler),
            (r"/category/update/([^/]+)", CategoryUpdateHandler),
            (r"/category/delete/([^/]+)", CategoryDeleteHandler)
        ]
        settings = dict(
                cookie_secret="TODO:CREATE_COOKIES_SECRET",
                template_path=os.path.join(os.path.dirname(__file__), "templates"),
                static_path=os.path.join(os.path.dirname(__file__), "static"),
                xsrf_cookies=True,
                debug=True,
                )
        self.db = dbhelper.POOL,
        tornado.web.Application.__init__(self, handlers, **settings)
                
def runserver():
    tornado.options.parse_command_line()
    application = Application()
    http_server=tornado.httpserver.HTTPServer(application)
    http_server.listen(options.port)
    tornado.ioloop.IOLoop.current().start()
    
if __name__ == "__main__":
	runserver()