#coding:utf-8
import tornado.web
import tornado.ioloop
import tornado.httpserver
import tornado.options
import os.path
import sqlite3
import time
from tornado.options import define, options

conn = sqlite3.connect('chatroom.db')
cur  = conn.cursor()

# Login and set cookie
class LoginHandler(tornado.web.RequestHandler):
	# Check user_name and password
	def check_user(self, username, password):
		sql = "select * from user where username = '%s' and password = '%s' " %(username, password)
		cur.execute(sql)

		if cur.fetchall():
			return True;
		return False;

	def get(self):
		cookie_user = self.get_secure_cookie("username")
		self.render('login.html',cookieUser=cookie_user,Error=False)
			
	def post(self):
		username = self.get_argument('username')
		password = self.get_argument('password')
		if self.check_user(username, password): # user_name and password correct
			self.set_secure_cookie("username", username, 1)
			cookie_user = self.get_argument('username')
			self.render('login.html', cookieUser=cookie_user,Error=False)

		else: # password not correct
			self.render('login.html',cookieUser=None,Error=True)

# Log out
class LogoutHandler(tornado.web.RequestHandler):
	def get(self):
		self.clear_all_cookies()
		time.sleep(1)
		self.redirect("/login")


