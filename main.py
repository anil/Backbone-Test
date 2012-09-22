import tornado.httpserver
import tornado.ioloop
import tornado.options
import tornado.web
import os
import mongoengine
from tornado.options import define, options
import json

define("port", default=8888, help="run on the given port", type=int)

class Anon_User(mongoengine.Document):
    num_clicks = mongoengine.IntField()


class MainHandler(tornado.web.RequestHandler):
    def get(self):
        if self.get_cookie("id") == None:
          anon_user = Anon_User()
          anon_user.num_clicks = 0
          anon_user.save()
          self.set_cookie("id", str(anon_user.id))

        self.render("index.html")

class AnonUserRESTHandler(tornado.web.RequestHandler):
    def get(self):
       anon_user_id = self.get_cookie("id")
       if anon_user_id != None:
         anon_user = Anon_User.objects(id=anon_user_id).first()
         my_response = {}
         my_response["id"] = str(anon_user.id)
         my_response["num_clicks"] = anon_user.num_clicks
         self.write(json.dumps(my_response))
       else:
         self.write("didn't get it")

    def put(self): 
       data = json.loads(self.request.body)
       print data
       anon_user = Anon_User.objects(id=data["id"]).first()
       anon_user.num_clicks = data["num_clicks"]
       anon_user.save()
       self.write("success")

def main():

    handlers = [
        (r"/", MainHandler),
        (r"/api/v1/anon_user/", AnonUserRESTHandler)
    ]

    settings = dict(
       template_path=os.path.join(os.path.dirname(__file__), "templates"),
       static_path=os.path.join(os.path.dirname(__file__), "static"),
       debug=True
    )

    tornado.options.parse_command_line()
    application = tornado.web.Application(handlers,
        **settings
    )
    mongoengine.connect('backbone')
    http_server = tornado.httpserver.HTTPServer(application)
    http_server.listen(options.port)
    tornado.ioloop.IOLoop.instance().start()


if __name__ == "__main__":
    main()


