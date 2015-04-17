import pymongo
from github import Github, BadCredentialsException

from secrets import *


def add_user(access_token, group_name):

    # get access token and generate user
    g1 = Github(access_token)
    u1 = None
    try:
        u1 = g1.get_user()
    # if user cannot be generated, quit immediately
    except BadCredentialsException:
        return False

    # if user exists, check to see if the user is already
    # subscribed to the requested group
    if user_exists(u1.id):
        userlists = get_database().users.find_one({'id': u1.id})['lists']
        if group_name in userlists:
            return True

    # get all users in requested group
    for user in get_database().users.find({'status': 'working',
                                           'lists': {
                                               '$in': [group_name]}}):

        # generate user for each user in group and attempt
        # to have users follow each other
        g2 = Github(user['access_token'])

        try:
            u2 = g2.get_user()
            u2.add_to_following(g2.get_user(u1.login))
            u1.add_to_following(g1.get_user(u2.login))
        except BadCredentialsException:
            get_database().users.update({
                'access_token': user['access_token']}, {
                '$set': {
                    'status': 'broken'}})

    # if user exists already, just update them as
    # being subscribed to the new list
    if user_exists(u1.id):
        get_database().users.update({
            'id': u1.id}, {
            '$set': {
                'access_token': access_token,
                'username': u1.login},
            '$push': {
                'lists': group_name}})

    # otherwise, add them as a new user
    else:
        get_database().users.insert({
            'access_token': access_token,
            'username': u1.login,
            'id': u1.id,
            'status': 'working',
            'lists': [group_name]})
    return True


def get_database():
    client = pymongo.MongoClient(os.environ.get('MONGODB_URL'))
    return client.githubusers


def user_exists(userid):
    if get_database().users.find_one({'id': userid}) is None:
        return False
    return True