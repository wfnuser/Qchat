#coding:utf-8
import tornado.web
import tornado.ioloop
import tornado.httpserver
import tornado.options
import json
import tornado.web
import tornado.gen
import tornadoredis
from tornado.escape import json_encode
import os.path
import sqlite3
import datetime
import time
import common
from tornado.options import define, options
import re


conn = sqlite3.connect('chatroom.db')
cur  = conn.cursor()

c = tornadoredis.Client()
c.connect()

# chatRoom list
class ChatRoomHandler(tornado.web.RequestHandler):

	def get_current_user(self):
		return self.get_secure_cookie("username")

	def get(self):
		cookie_user = self.get_secure_cookie("username")
		roomlist = common.getRoomList()

		if cookie_user:
			# usertype = common.get_usertype(cookie_user)
			self.render('chatroom.html', cookieUser=cookie_user, Error=False,
						roomlist=roomlist)
		else:
			self.render('login.html', cookieUser=None, Error = False)
			
	def post(self):
		return

# Create Room
class CreateRoomHandler(tornado.web.RequestHandler):

	# Check room name
	def check_is_userd(self,roomname):
		sql = "select roomname from room where roomname = '%s' " %(roomname)
		cur.execute(sql)
		if cur.fetchall():
			return True;
		return False;

	def get(self):
		cookie_user = self.get_secure_cookie("username")
		if cookie_user:
			self.render('createroom.html', cookieUser=cookie_user, Error=False)
		else:
			self.render('login.html', cookieUser=None, Error = False)

	# create new room
	def post(self):
		roomname = self.get_argument('roomname')
		username = self.get_secure_cookie('username')
		
		# roomname already been taker
		if self.check_is_userd(roomname):
			self.render('createroom.html', cookieUser=username, Error=True)
			return

		sql = "select userid from user where username = '%s' " % (username)
		cursor = conn.execute(sql)
		for row in cursor:
			userid = row[0]
		# Create
		sql = "insert into room (roomname, created_time, owner_id) \
				values('%s', datetime('now'), %d)" %(roomname, userid)
		conn.execute(sql)
		conn.commit()
		self.redirect("/chatroom")

#Chat
class ChatHandler(tornado.web.RequestHandler):

	def get(self):
		uri_list = self.request.uri.split('/')
		roomid = int(uri_list[-1])

		self.set_secure_cookie("roomid", str(roomid),1)
		cookie_user = self.get_secure_cookie("username")
		if cookie_user:
			# usertype = common.get_usertype(cookie_user)
			roominfo = common.getRoomInfo(roomid)
			if roominfo is None:
				# jump to 404
				self.render("404err.html")
			# success to room
			else:
				sql = "select username,msg,created_time from message where roomid = %d order by msgid \
						desc limit 100" % (roomid)
				cursor = conn.execute(sql)
				#last 100 msgs
				msginfoList = list(cursor.fetchall())
				msginfoList.reverse()
				# for each in msginfoList:
					# each[1] = re.sub("\[em_([0-9]*)\]", '<img src="/static/face/1.gif" border="0" />', each[1])
				
				self.render('chat.html', cookieUser=cookie_user,
							roominfo=roominfo, msginfo=msginfoList)
		else:
			self.render('login.html', cookieUser=None, Error = False)

	@tornado.web.asynchronous
	def post(self):
		username = self.get_secure_cookie("username")
		msg = self.get_argument("msg")
		
		data = json_encode({'name':username, 'msg':msg})
		roomchannel = str(self.get_secure_cookie('roomid'))
		
		sql = "insert into message(roomid,username,msg,created_time)\
			   values(%d,'%s','%s',datetime('now'))" % (int(roomchannel),username,msg)
		conn.execute(sql)
		conn.commit()

		# publish msg to Redis
		c.publish(roomchannel, data)
		
		self.write(json_encode({'result':True}))
		self.finish()
