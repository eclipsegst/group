import tornado.gen

from base_handler import BaseHandler

class GroupOwnHandler(BaseHandler):
    @tornado.gen.coroutine
    def get(self, id):
        cur = yield self.db.execute("select groups.id, groups.name, category.name, groups.description, groups.created_by, groups.timestamp from groups left join category on groups.category_id=category.id where groups.created_by=" + str(id))
        grouplist = []
        for row in cur:
            dict = {'id':str(row[0]), 'name':row[1], 'category_id':str(row[2]), 'description':str(row[3]), 'created_by':str(row[4]), 'created_date':str(row[5])}
            grouplist.append(dict)
        cur.close()
        list = grouplist
        self.render("group_own.html", groups=list)
        
class GroupNewHandler(BaseHandler):
    @tornado.gen.coroutine
    def get(self):
        cur = yield self.db.execute("select * from category")
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
        cur = yield self.db.execute(sql_query)
        self.redirect("/")
        
class GroupUpdateHandler(BaseHandler):
    @tornado.gen.coroutine
    def get(self, id):
        #handle incorrect id
        cur = yield self.db.execute("select * from groups where id=" + str(id))
        row = cur.fetchall()[0]
        cur.close()
        group = {'id':str(row[0]), 'name':row[1], 'created_by':str(row[2])}
        self.render("group_update.html", group=group)
    
    @tornado.gen.coroutine
    def post(self, id):
        #handle incorrect id
        group_name = self.get_argument("name")
        sql_query = "update groups set name='" + group_name + "' where id=" + str(id)
        cur = yield self.db.execute(sql_query)
        self.redirect("/")
    
class GroupDeleteHandler(BaseHandler):    
    @tornado.gen.coroutine
    def post(self, id):
        #handle incorrect id
        cur = yield self.db.execute("delete from groups where id=" + str(id))
        self.redirect("/")