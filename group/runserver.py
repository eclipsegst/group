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
        cur = yield self.db[0].execute("select groups.id, groups.name, category.name, groups.description, groups.created_by, groups.timestamp from groups left join category on groups.category_id=category.id")
        grouplist = []
        for row in cur:
            dict = {'id':str(row[0]), 'name':row[1], 'category_id':str(row[2]), 'description':str(row[3]), 'created_by':str(row[4]), 'created_date':str(row[5])}
            grouplist.append(dict)
        cur.close()
        self.render("index.html", groups=grouplist)

class GroupOwnHandler(BaseHandler):
    @tornado.gen.coroutine
    def get(self, id):
        cur = yield self.db[0].execute("select groups.id, groups.name, category.name, groups.description, groups.created_by, groups.timestamp from groups left join category on groups.category_id=category.id where groups.created_by=" + str(id))
        grouplist = []
        for row in cur:
            dict = {'id':str(row[0]), 'name':row[1], 'category_id':str(row[2]), 'description':str(row[3]), 'created_by':str(row[4]), 'created_date':str(row[5])}
            grouplist.append(dict)
        cur.close()
        list = grouplist
        self.render("group_own.html", groups=list)
        
class GroupHandler(BaseHandler):
    @tornado.gen.coroutine
    def get(self):
        cur = yield self.db[0].execute("select * from category")
        category_list = []
        for row in cur:
            dict = {'id':str(row[0]), 'name':row[1]}
            category_list.append(dict)
        cur.close()
        list = category_list
        self.render("group_new.html", categories=list)
    
    @tornado.gen.coroutine
    def post(self):
        group_name = self.get_argument("name")
        category = self.get_argument("category")
        description = self.get_argument("description")
        print(category)
        sql_query = "insert into groups (name, category_id, description, created_by) values('" + group_name + "', " + category + ", '" + description + "', 1)"
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

# User have an admin role can create/update/delete category
class CategoryHandler(BaseHandler):
    @tornado.gen.coroutine
    def get(self):
        cur = yield self.db[0].execute("select * from category")
        category_list = []
        for row in cur:
            dict = {'id':str(row[0]), 'name':row[1], 'created_by':str(row[2]), 'created_date':str(row[3])}
            category_list.append(dict)
        cur.close()
        list = category_list
        self.render("categories.html", categories=list)

class CategoryNewHandler(BaseHandler):
    @tornado.gen.coroutine
    def get(self):
        self.render("category_new.html")
    
    @tornado.gen.coroutine
    def post(self):
        category_name = self.get_argument("name")
        print(category_name)
        #TODO: Get current user id, handle duplicate category
        sql_query = "insert into category (name, created_by) values('" + category_name + "', 1)"
        cur = yield self.application.db[0].execute(sql_query)
        self.redirect("/category")   
        
class CategoryUpdateHandler(BaseHandler):
    @tornado.gen.coroutine
    def get(self, id):
        #handle incorrect id
        cur = yield self.db[0].execute("select * from category where id=" + str(id))
        row = cur.fetchall()[0]
        cur.close()
        category = {'id':str(row[0]), 'name':row[1], 'created_by':str(row[2])}
        self.render("category_update.html", category=category)
    
    @tornado.gen.coroutine
    def post(self, id):
        #handle incorrect id
        category_name = self.get_argument("name")
        sql_query = "update category set name='" + category_name + "' where id=" + str(id)
        cur = yield self.application.db[0].execute(sql_query)
        self.redirect("/category")
        
class CategoryDeleteHandler(BaseHandler):    
    @tornado.gen.coroutine
    def post(self, id):
        #handle incorrect id
        cur = yield self.db[0].execute("delete from category where id=" + str(id))
        self.redirect("/category")
             
class Application(tornado.web.Application):
    def __init__(self):
        handlers = [(r"/", MainHandler),
            (r"/group/own/([^/]+)", GroupOwnHandler),
            (r"/group/new", GroupHandler),
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