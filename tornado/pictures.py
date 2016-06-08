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
from datetime import timedelta
import time
import common
from tornado.options import define, options
import re
import urllib
import urllib2
import os

try:
    from HTMLParser import HTMLParser
    from urlparse import urljoin, urldefrag
except ImportError:
    from html.parser import HTMLParser
    from urllib.parse import urljoin, urldefrag
from tornado import httpclient, queues



conn = sqlite3.connect('chatroom.db')
cur  = conn.cursor()

c = tornadoredis.Client()
c.connect()

# Picture page list
class PictureHandler(tornado.web.RequestHandler):

	def get(self):
		cookie_user = self.get_secure_cookie("username")

		picturelist = []
		for files in os.walk("./static/pictures/lawa"):
			for name in files:
				picturelist = name
		picturelist = picturelist[1:]
		if cookie_user:
			self.render('picture.html', cookieUser=cookie_user, pictureList = picturelist, Error=False)
		else:
			self.render('login.html', cookieUser=None, Error = False)
			


# Crawling
class CrawHandler(tornado.web.RequestHandler):

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


# base_url = 'https://douban.com'
base_url = 'https://bbs.sjtu.edu.cn/bbstdoc,board,PPPerson.html'

concurrency = 10
picturehreflist = []
userhreflist = []


@tornado.gen.coroutine
def get_pictures_from_url(url):

    try:
        # response = yield httpclient.AsyncHTTPClient().fetch(url)
        http_header   = {'User-Agent':'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/34.0.1847.116 Safari/537.36'}
        http_request  = tornado.httpclient.HTTPRequest(url=url,method='GET',headers=http_header, use_gzip=True, connect_timeout=200, request_timeout=600)
        # http_client   = tornado.httpclient.HTTPClient()
        response = yield httpclient.AsyncHTTPClient().fetch(http_request)
        print('fetched %s' % url)

        html = response.body if isinstance(response.body, str) \
            else response.body.decode("gbk")

        html = html.decode("gbk")

        pattern = re.compile('(?<=href=")[\w,?,=]*(?=")')
        userhreflist = pattern.findall(html)
        pattern = re.compile('(?<=href=)[\w,,]*.html(?=>)')
        picturehreflist = pattern.findall(html)
        pattern = re.compile(r'(?<=<a href=(bbstcon,board,PPPerson,reid,([0-9][0-9][0-9][0-9][0-9][0-9][0-9][0-9][0-9][0-9]).html>))[^<]*')
        titlelist = pattern.findall(html)
        # pattern = re.compile(r'(?<=href=")[\w,?,=]*')
        # hreflist = re.search(r'(?<=href=")[\w,?,=]*', '<tr><td>5105<td><td><a href="bbsqry?userid=lawa">lawa</a><td>Jun  1 00:16<td><a href=bbstcon,board,PPPerson,reid,1464711364.html>○ 广末凉子 # 6 </a>(3回复)<tr><td>5106<td><td><a href="bbsqry?userid=lawa">lawa</a><td>Jun  1 00:16<td><a href=bbstcon,board,PPPerson,reid,1464711411.html>○ 佟丽娅 # 10 </a>(0回复)<tr><td>5107<td><td><a href="bbsqry?userid=lawa">lawa</a><td>Jun  1 00:17<td><a href=bbstcon,board,PPPerson,reid,1464711464.html>○ 俞飞鸿 # 2 </a>(0回复)<tr><td>5108<td><td><a href="bbsqry?userid=lawa">lawa</a><td>Jun  1 00:19<td><a href=bbstcon,board,PPPerson,reid,1464711567.html>○ 坛蜜 # 1 </a>(')
        print(userhreflist)
        print(picturehreflist)
        print(titlelist)
        # for eachhref in hreflist:
        # 	print(eachhref)
        # print(html)	

        urls = [urljoin(url, remove_fragment(new_url))
                for new_url in get_links(html)]

        for index,eachhref in enumerate(picturehreflist):
        		if(index >= (len(picturehreflist)-1)): break
        		tmpurl = eachhref
        		tmpname = userhreflist[index+2]
        		tmpurl = 'https://bbs.sjtu.edu.cn/'+tmpurl
        		http_request  = tornado.httpclient.HTTPRequest(url=tmpurl,method='GET',headers=http_header, use_gzip=True, connect_timeout=200, request_timeout=600)
        		response = yield httpclient.AsyncHTTPClient().fetch(http_request)
        		print('fetched %s' % tmpurl)
        		html = response.body if isinstance(response.body, str) \
        				else response.body.decode("gbk")
        		html = html.decode("gbk")

        		# print(html)
        		pattern = re.compile('(?<=SRC=")[\w,.,/]*(?=")')
        		imglist = pattern.findall(html)

        		save_path = './static/pictures/'
        		tmp_savepath = save_path + tmpname
        		try:
        			os.makedirs(tmp_savepath, 0755)
        		except Exception as e:
        			print('Already exists!')
        		# os.makedirs( tmp_savepath, 0755 );


        		for eachimg in imglist:
        				imgurl = 'https://bbs.sjtu.edu.cn/'+eachimg
        				print(imgurl)
        				fileName = tmp_savepath + '/' + eachimg.split('/')[3]
        				print("save as "+fileName)
        				urllib.urlretrieve(imgurl,fileName)
        				print "Finished download \n"



        		print(tmpurl)
        		print(tmpname)
        		print(imglist)
        		print("\n\n")



    except Exception as e:
        print('Exception: %s %s' % (e, url))
        raise tornado.gen.Return([])

    raise tornado.gen.Return(urls)


def remove_fragment(url):
    pure_url, frag = urldefrag(url)
    return pure_url


def get_links(html):
    class URLSeeker(HTMLParser):
        def __init__(self):
            HTMLParser.__init__(self)
            self.urls = []

        def handle_starttag(self, tag, attrs):
            href = dict(attrs).get('href')
            if href and tag == 'a':
                self.urls.append(href)

    url_seeker = URLSeeker()
    url_seeker.feed(html)
    return url_seeker.urls


@tornado.gen.coroutine
def main():
    q = queues.Queue()
    start = time.time()
    fetching, fetched = set(), set()

    newq = queues.Queue()
    
    @tornado.gen.coroutine
    def fetch_url():
        current_url = yield q.get()
        try:
            if current_url in fetching:
                return

            print('fetching %s' % current_url)
            fetching.add(current_url)
            urls = yield get_pictures_from_url(current_url)
            fetched.add(current_url)

            for new_url in urls:
                # Only follow links beneath the base URL
                if new_url.startswith('base_url'):
                    yield q.put(new_url)

        finally:
            q.task_done()

    @tornado.gen.coroutine
    def download_pic():
    		current_url = yield newq.get()
    		try:
    				print(current_url)
    		finally:
    			newq.task_done()


    @tornado.gen.coroutine
    def downloader():
        while True:
            yield download_pic()

    @tornado.gen.coroutine
    def worker():
        while True:
            yield fetch_url()


    q.put(base_url)


    # Start workers, then wait for the work queue to be empty.
    for _ in range(concurrency):
        worker()
    yield q.join(timeout=timedelta(seconds=300))
    assert fetching == fetched
    print('Done in %d seconds, fetched %s URLs.' % (
        time.time() - start, len(fetched)))


    # time.sleep(5)
    # for index,eachhref in enumerate(picturehreflist):
    # 	newq.put({url:eachhref,name:userhreflist[index+2]})
    # for _ in range(concurrency):
    # 		downloader()




if __name__ == '__main__':
    import logging
    logging.basicConfig()
    io_loop = tornado.ioloop.IOLoop.current()
    io_loop.run_sync(main)
