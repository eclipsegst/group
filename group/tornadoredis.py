import tornado.web
import redis
from hashlib import md5

class Login(tornado.web.RequestHandler):
        def initialize(self):
                ## Initialize redis
                self.r = redis.Redis("localhost")

                ## Add users
                self.r.sadd("users", 'bob')
                self.r.set('bob', md5('bob').hexdigest())
                self.r.sadd("users", 'bob')
                self.r.set('clara', md5('clara').hexdigest())

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

application = tornado.web.Application([
        (r"/login", Login)],
        debug=True)

if __name__ == '__main__':
        application.listen(8888)
        tornado.ioloop.IOLoop.instance().start()
