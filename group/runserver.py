import os
import tornado.gen
import tornado.httpserver
import tornado.ioloop
import tornado.web
import tornado_mysql

from tornado.options import define, options
define("port", default=8888, help="run on the given port", type=int)

import dbhelper

class BaseHandler(tornado.web.RequestHandler):
    @property
    def db(self):
        return self.application.db

class MainHandler(BaseHandler):
    @tornado.gen.coroutine
    def get(self):
        cur = yield self.db[0].execute("select * from groups")
        grouplist = []
        for row in cur:
            dict = {'id':str(row[0]), 'name':row[1], 'category_id':str(row[2]), 'description':str(row[3]), 'created_by':str(row[4]), 'created_date':str(row[5])}
            grouplist.append(dict)
        cur.close()
        list = grouplist
        self.render("index.html", groups=list)

class GroupHandler(BaseHandler):
    @tornado.gen.coroutine
    def get(self):
        self.render("group_new.html")
    
    @tornado.gen.coroutine
    def post(self):
        group_name = self.get_argument("name")
        category = self.get_argument("category")
        description = self.get_argument("description")
        print(category)
        sql_query = "insert into groups (name, category_id, description, created_by) values('" + group_name + "', " + category + ", '" + description + "', 2)"
        cur = yield self.application.db[0].execute(sql_query)
        self.redirect("/")
        
class GroupUpdateHandler(BaseHandler):
    @tornado.gen.coroutine
    def get(self, id):
        #handle incorrect id
        cur = yield self.db[0].execute("select * from groups where id=" + str(id))
        row = cur.fetchall()[0]
        cur.close()
        group = {'id':str(row[0]), 'name':row[1], 'created_by':str(row[2])}
        self.render("group_update.html", group=group)
    
    @tornado.gen.coroutine
    def post(self, id):
        #handle incorrect id
        group_name = self.get_argument("name")
        sql_query = "update groups set name='" + group_name + "' where id=" + str(id)
        cur = yield self.application.db[0].execute(sql_query)
        self.redirect("/")

class GroupDeleteHandler(BaseHandler):    
    @tornado.gen.coroutine
    def post(self, id):
        #handle incorrect id
        cur = yield self.db[0].execute("delete from groups where id=" + str(id))
        self.redirect("/")

class Application(tornado.web.Application):
    def __init__(self):
        handlers = [(r"/", MainHandler),
            (r"/group", GroupHandler),
            (r"/group/update/([^/]+)", GroupUpdateHandler),
            (r"/group/delete/([^/]+)", GroupDeleteHandler)
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