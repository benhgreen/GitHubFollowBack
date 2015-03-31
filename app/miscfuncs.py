import sys, os
import pymongo
from github import Github
from secrets import *


def processCallback(args):

	# make sure args are all there
	for arg in {'code', 'state'}:
		if arg not in args:
			return False

	# check state
	if not args['state'] == STATE:
		return False

	return True

def addUser(access_token):
	g1 = GitHub(access_token)
	u1 = g1.get_user()

	if userExists(u1.id):
		getDatabase().users.update({'id': u1.id}, {'access_token': access_token, 'username': u1.login})
		return


	for user in getDatabase().users.find():
		g2 = GitHub(user['access_token'])
		u2 = g2.get_user()

		u2.add_to_following(u1)
		u1.add_to_following(u2)

	getDatabase().users.insert({'access_token': access_token, 'username': u1.login, 'id': u1.id})
	

def getDatabase():
	client = pymongo.MongoClient(os.environ.get('MONGODB_URL'))
	return client.githubusers

def userExists(id):
	if getDatabase().users.find({'id': id}) is not None:
		return False
	return True