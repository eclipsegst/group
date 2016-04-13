import tornado.gen

from base_handler import BaseHandler

# User have an admin role can create/update/delete category
class CategoryHandler(BaseHandler):
    @tornado.gen.coroutine
    def get(self):
        cur = yield self.db.execute("select * from category")
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
        cur = yield self.db.execute(sql_query)
        self.redirect("/category")   
        
class CategoryUpdateHandler(BaseHandler):
    @tornado.gen.coroutine
    def get(self, id):
        #handle incorrect id
        cur = yield self.db.execute("select * from category where id=" + str(id))
        row = cur.fetchall()[0]
        cur.close()
        category = {'id':str(row[0]), 'name':row[1], 'created_by':str(row[2])}
        self.render("category_update.html", category=category)
    
    @tornado.gen.coroutine
    def post(self, id):
        #handle incorrect id
        category_name = self.get_argument("name")
        sql_query = "update category set name='" + category_name + "' where id=" + str(id)
        cur = yield self.db.execute(sql_query)
        self.redirect("/category")
        
class CategoryDeleteHandler(BaseHandler):    
    @tornado.gen.coroutine
    def post(self, id):
        #handle incorrect id
        cur = yield self.db.execute("delete from category where id=" + str(id))
        self.redirect("/category")