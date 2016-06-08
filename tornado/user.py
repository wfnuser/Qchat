#coding:utf-8
import tornado.web
import tornado.ioloop
import tornado.httpserver
import tornado.options

import os.path
import sqlite3
import datetime
import time

import common
from tornado.options import define, options

conn = sqlite3.connect('chatroom.db')
cur  = conn.cursor()

# Modify user info
class ModifyHandler(tornado.web.RequestHandler):
	
	def get(self):
		cookie_user = self.get_secure_cookie("username")
		if cookie_user is None:
			self.redirect('/login')
		self.render('modify.html',cookieUser=cookie_user)
	
	def post(self):
		username = self.get_secure_cookie("username")
		if username is None:
			self.redirect('/login')
		password = self.get_argument('password')
		rep_password = self.get_argument('rep_password')
		email = self.get_argument('email')
		phone = self.get_argument('phone')
		if password != rep_password:
			self.write("Wrong Password")
			self.render('modify.html',cookieUser=username)
		sql = "update user set password='%s', email='%s', phone='%s' where username ='%s' "\
				 %(password, email, phone, username)
		conn.execute(sql)
		conn.commit()
		self.write("Success")
		self.redirect('/chatroom')


