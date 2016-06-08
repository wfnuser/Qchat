#coding:utf-8
import sqlite3

conn = sqlite3.connect('chatroom.db')
cur  = conn.cursor()

# get user type (admin / common user)
# def get_usertype(username):
# 	sql = "select usertype from user where username = '%s' limit 1" %(username)
# 	cur.execute(sql)
# 	usertype = cur.fetchone()
# 	if not usertype:
# 		return None
# 	return usertype[0]

# return [roomlist,room_owner]
def getRoomList():
	sql = "select room.roomid,room.roomname,room.created_time,room.owner_id,user.username \
			from room,user where room.owner_id == user.userid"

	cursor = conn.execute(sql)
	roomlist = list(cursor.fetchall())
	return roomlist

# get room info by user roomid
def getRoomInfo(roomid):
	# check roomid is legal
	sql = "select * from room where roomid = %d" % (roomid)
	cursor = conn.execute(sql)
	ret = cursor.fetchone()
	if ret is None:
		return None
		
	# roomid range from [1,Max_roomid]	
	sql = "select room.roomid,room.roomname,room.created_time,room.owner_id,user.username \
			from room,user where room.roomid = %d and room.owner_id == user.userid" %(roomid)
	cursor = conn.execute(sql)
	roominfo = list(cursor.fetchone())
	return roominfo


