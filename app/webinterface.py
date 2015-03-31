from tornado.wsgi import WSGIContainer
from tornado.httpserver import HTTPServer
from tornado.ioloop import IOLoop

import requests
from flask import Flask, render_template, redirect, request
from urlparse import parse_qs
from secrets import *
from miscfuncs import *
app = Flask(__name__)
app.config.from_object('config')

@app.route('/', methods=['GET', 'POST'])
def root():
	return render_template('base.html', welcome='welcome')

@app.route('/callback/', methods=['GET', 'POST'])
def callback():

	# try to get access token
	r = requests.post('https://github.com/login/oauth/access_token?client_id=%s&client_secret=%s&code=%s' % (GITHUB_CLIENT_ID, GITHUB_CLIENT_SECRET, request.args['code']))

	parsed_response = parse_qs(r.content)

	if not 'access_token' in parsed_response:
		print 'did not get acccess from github'
		return ':('

	addUser(parsed_response['access_token'][0])

	return redirect('/success/')

@app.route('/success/', methods=['GET', 'POST'])
def success():
	return render_template('base.html', success='success')

if __name__ == '__main__':
	http_server = HTTPServer(WSGIContainer(app))
	http_server.listen(5000)
	IOLoop.instance().start()