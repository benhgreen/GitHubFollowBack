import sys, os
import pymongo
from github import Github, GithubException, BadCredentialsException
from secrets import *

def addUser(access_token):
	g1 = Github(access_token)
	u1 = None
	try:
		u1 = g1.get_user()
	except BadCredentialsException, e:
		return False

	if userExists(u1.id):
		getDatabase().users.update({'id': u1.id}, {'access_token': access_token, 'username': u1.login})
		return True


	for user in getDatabase().users.find({'status': 'working'}):
		g2 = Github(user['access_token'])

		try:
			u2 = g2.get_user()
			u2.add_to_following(u1.login)
			u1.add_to_following(u2.login)
		except BadCredentialsException, e:
			getDatabase().users.update({'access_token': user['access_token']}, {'$set': {'status': 'broken'}})


	getDatabase().users.insert({'access_token': access_token, 'username': u1.login, 'id': u1.id, 'status': 'working'})

	return True
	

def getDatabase():
	client = pymongo.MongoClient(os.environ.get('MONGODB_URL'))
	return client.githubusers

def userExists(id):
	if getDatabase().users.find({'id': id}) is not None:
		return False
	return True