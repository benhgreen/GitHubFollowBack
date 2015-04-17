from tornado.wsgi import WSGIContainer
from tornado.httpserver import HTTPServer
from tornado.ioloop import IOLoop

import requests
from flask import Flask, render_template, redirect, request
from urlparse import parse_qs
from forms import SubmitForm
from secrets import *
from miscfuncs import *

app = Flask(__name__)
app.config.from_object('config')


@app.route('/', methods=['GET', 'POST'])
def root():
    form = SubmitForm()
    if form.validate_on_submit():
        return redirect("https://github.com/login/oauth/authorize?"
                        "client_id=%s"
                        "&scope=user:follow"
                        "&state=%s" % (GITHUB_CLIENT_ID, form.group.data))
    return render_template('base.html', welcome='welcome', form=form)


@app.route('/callback/', methods=['GET', 'POST'])
def callback():
    print "Callback received:"
    for arg in request.args:
        print "%s: %s" % (arg, request.args[arg])
    print "\n"

    if 'state' not in request.args:
        return ':('

    # try to get access token
    r = requests.post(
        'https://github.com/login/oauth/access_token?'
        'client_id=%s&client_secret=%s&code=%s' % (
            GITHUB_CLIENT_ID, GITHUB_CLIENT_SECRET, request.args['code']))

    parsed_response = parse_qs(r.content)

    if 'access_token' not in parsed_response:
        print 'did not get access from github'
        return ':('

    add_user(parsed_response['access_token'][0], request.args['state'])

    return redirect('/success/')


@app.route('/success/', methods=['GET', 'POST'])
def success():
    return render_template('base.html', success='success')


if __name__ == '__main__':
    http_server = HTTPServer(WSGIContainer(app))
    http_server.listen(5000)
    IOLoop.instance().start()