#coding:utf-8

import tornado.web
import tornado.ioloop
import tornado.httpserver
import tornado.options

import os.path
import sqlite3
import datetime
import time

from tornado.options import define, options

conn = sqlite3.connect('chatroom.db')
cur  = conn.cursor()

# Register
class RegisterHandler(tornado.web.RequestHandler):
	
	def check_is_used(self, username):
		sql = "select username from user where username = '%s' " %(username)
		cur.execute(sql)

		if cur.fetchall():
			return True;
		return False;

	def get(self):
		self.render('register.html', Error=False, cookieUser=None)
	
	def post(self):
		username = self.get_argument('username')
		password = self.get_argument('password')
		rep_password = self.get_argument('rep_password')
		email = self.get_argument('email','null')
		phone = self.get_argument('phone','null')
		if password != rep_password:
			self.write("Wrong password!")
			self.render('register.html', Error=True, cookieUser=None)

		if not self.check_is_used(username):
			sql = "insert into user (username, password, registed_time, email, phone) \
				   values ('%s', '%s', datetime('now'), '%s', '%s')" %(username, password, email, phone)
			conn.execute(sql)
			conn.commit()
			self.write("Success!")
			self.set_secure_cookie("username", username,1)
			cookie_user = self.get_argument('username')
			self.render('login.html', cookieUser=cookie_user)
		else:
			self.render('register.html',Error=True, cookieUser=None)


