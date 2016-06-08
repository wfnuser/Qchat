#coding: utf-8

import random
import time
import sys
import tornado.web
import tornado.gen
import tornadoredis
from tornado.escape import json_encode


class LongPollingHandler(tornado.web.RequestHandler):

  # Connect to Redis 
  def initialize(self):
    self.client = tornadoredis.Client()
    self.client.connect()

  def get_roomchannel(self):
    roomchannel = self.get_secure_cookie("roomid")
    return str(roomchannel)

  @tornado.web.asynchronous
  def get(self):
    self.get_data()

  @tornado.web.asynchronous
  def post(self):
    self.get_data()

  # Subscribe Redis msg
  @tornado.gen.engine
  def subscribe(self):
    yield tornado.gen.Task(self.client.subscribe, self.get_roomchannel())
    self.client.listen(self.on_message)
  
  def get_data(self):
    if self.request.connection.stream.closed():
      print(' Maybe lost! ')
      return
       
    try :
      self.subscribe()
    except Exception, e :
      print(e,__file__,sys._getframe().f_lineon)
      pass;

    # Set Time limit as 60 sec
    num = 60
    self.time_handler = tornado.ioloop.IOLoop.instance().add_timeout(
      time.time()+num,
      lambda: self.on_timeout(num)
    )

  def on_timeout(self, num):
    self.time_handler = None
    self.send_data(json_encode({'name':'', 'msg':''}))
    if (self.client.connection.connected()):
      self.client.disconnect()
  
  # Send data 
  def send_data(self, data):
    if self.request.connection.stream.closed():
      return

    self.set_header('Content-Type', 'application/json; charset=UTF-8')
    self.write(data)
    self.finish()

  # get Redis msg
  def on_message(self, msg):
    if (msg.kind == 'message'):
      self.send_data(str(msg.body))
    elif (msg.kind == 'unsubscribe'):
      self.client.disconnect()

  def remove_time_handler(self):
    if self.time_handler :
      tornado.ioloop.IOLoop.instance().remove_timeout(self.time_handler)
      self.time_handler = None

  def on_finish(self):
    self.remove_time_handler()
    if (self.client.subscribed):
      self.client.unsubscribe(self.get_roomchannel());

  def on_connection_close(self):
    self.finish()
