#coding:utf-8
import tornado.web
import tornado.ioloop
import tornado.httpserver
import tornado.options
import os.path
import sqlite3
import datetime
import time

from chatroom import ChatRoomHandler, CreateRoomHandler, ChatHandler
from login 	  import LoginHandler, LogoutHandler
from register import RegisterHandler
from user 	  import ModifyHandler
from pictures import PictureHandler
from longpolling import LongPollingHandler
from tornado.options import define, options

define("port", default=8890, help="run on given port", type=int)

class Application(tornado.web.Application):
	def __init__(self):
		handlers = [(r'/login', LoginHandler),
					(r'/',LoginHandler),
					(r'/logout', LogoutHandler),
					(r'/register', RegisterHandler),
					(r'/chatroom', ChatRoomHandler),
					(r'/modify', ModifyHandler),
					(r'/create', CreateRoomHandler),
					(r'/room/\d*', ChatHandler),
					(r'/longpolling',LongPollingHandler),
					(r'/picture',PictureHandler),

					]
		settings = dict(
					cookie_secret =
					"bZJc2sWbQLKos6GkHn/VB9oXwQt8S0R0kRvJ5/xJ89E=",
					template_path =
					os.path.join(os.path.dirname(__file__), "templates"),
					static_path =
					os.path.join(os.path.dirname(__file__), "static"),
					)
		tornado.web.Application.__init__(self, handlers, **settings)

if __name__ == "__main__":
	tornado.options.parse_command_line()
	http_server = tornado.httpserver.HTTPServer(Application())
	http_server.listen(options.port)
	print('server start on http://localhost:8890')
	tornado.options.parse_command_line()
	tornado.ioloop.IOLoop.instance().start()
