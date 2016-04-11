import tornado.web

class MainHandler(tornado.web.RequestHandler):
    def get(self):
        pool = self.application.pool
        cur = yield pool.execute("show tables;")
        print(cur)
        list = []
        self.render("index.html", groups=list)       
class GroupNewHandler(tornado.web.RequestHandler):
    def post(self):
        # global_group_buffer is used for local testing
        group = {
            "id":str(uuid.uuid4()),
            "name": self.get_argument("name"),
        }
        global_group_buffer.new_group([group])
       
        # open redis connection
        print("open redis connection")
        pool = redis.ConnectionPool(host='localhost')
        r = redis.StrictRedis(connection_pool=pool, charset="utf-8", decode_responses=True)
        # get group count
        print("get group count")
        group_count = r.get("group_count")
        if group_count is None:
            r.set("group_count", 0)
            group_count = r.get("group_count")
        count = int(group_count.decode("utf-8"))
        print(count)
        
        # create new group object and add to database
        print("create new group object and add to database")
        millis = int(round(time.time() * 1000))
        groupset_name = "group:" + str(count)
        groupset_content = {"name":self.get_argument("name"), "description":"This group" + str(count) + " is about...", "created_by":"user_id_" + str(count), "created_at":str(millis)}
        result = r.hmset(groupset_name, groupset_content)

        print("increase group count and add the new group hashset id to grouplis")
        # increase group count and add the new group hashset id to grouplis
        r.incr("group_count")
        r.lpush("group_list", groupset_name)
        print(int(r.get("group_count").decode("utf-8")))
        
        # retrieve grouplist
        print("get new group list")
        grouplist = r.lrange("group_list", 0, -1)
        print(grouplist)
        # retrieve group detail
        print("get group detail")
        for group in grouplist:
            group_hash_dict = r.hgetall(group)
            unidict = {k.decode('utf8'): v.decode('utf8') for k, v in group_hash_dict.items()}
            print(unidict)
            
        self.redirect("/group") 

class GroupUpdateHandler(tornado.web.RequestHandler):
    def get(self):
        self.write("group update")

class GroupDeleteHandler(tornado.web.RequestHandler):
    def get(self):
        self.write("group delete")

class GroupJoinHandler(tornado.web.RequestHandler):
    def get(self):
        self.write("group join")

class GroupLeaveHandler(tornado.web.RequestHandler):
    def get(self):
        self.write("group leave")
class Login(tornado.web.RequestHandler):
    def initialize(self):
        ## initialize redis
        self.r = redis.Redis("localhost")

        ## Add simple user example
        self.r.sadd("users", 'bob')
        self.r.set('bob', 'bob')
        self.r.sadd("users", 'bob')
        self.r.set('clara', 'clara')

    def get(self):
        self.render('login.html')

    def post(self):
        username = self.get_argument("username")
        password = self.get_argument("password")
        if self.r.sismember("users", username):
            if self.r.get(username) == password:
                self.write("Login successful!")
        else:
            self.write("Login Unsuccesful..")
            
handlers = [
	(r"/", MainHandler),
    (r"/group/new", GroupNewHandler),
    (r"/group/uodate", GroupUpdateHandler),
    (r"/group/delete", GroupDeleteHandler),
    (r"/group/join", GroupJoinHandler),
    (r"/group/leave", GroupLeaveHandler),
    (r"/login", Login)
]