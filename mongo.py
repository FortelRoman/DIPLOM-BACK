from datetime import date
from pymongo import MongoClient
import uuid

# cluster = MongoClient('mongodb+srv://fortelra19:fortelra19@devby.4yo2tlq.mongodb.net/?retryWrites=true&w=majority')
# db = cluster['DB_DEVBY']
# collection = db['COLLECTION_DEVBY']
# usersCollection = db['COLLECTION_USERS']

cluster = MongoClient('localhost', 27017)
db = cluster['DB_DEVBY']
collection = db['COLLECTION_DEVBY']
usersCollection = db['COLLECTION_USERS']


def findUserById(id):
    return usersCollection.find_one({"_id": id})

def findUserByLogin(login):
    return usersCollection.find_one({"login": login})

def addUser(username, login,  password, role):
    usersCollection.insert_one({
        '_id': str(uuid.uuid4()),
        'username': username,
        'login': login,
        'password': password,
        'role': role,
    })

def deleteProfileBD(userId):
    return usersCollection.delete_one({
        '_id': userId,
    }).deleted_count

def addItem(addDate, data):
    if (addDate.count):
        return collection.insert_one({
            '_id': str(uuid.uuid4()),
            'date': addDate,
            'records': data,
            'resource': 'devby.io',
        }).inserted_id
    return collection.insert_one({
        '_id': str(uuid.uuid4()),
        'date': str(date.today()),
        'records': data,
        'resource': 'devby.io',
    }).inserted_id


def getList():
    return collection.find().sort('date', -1)


def deleteItem(id):
    return collection.delete_one({'_id': id}).deleted_count


def getItem(id):
    return collection.find_one({'_id': id})


def getAllUsers():
    return usersCollection.find()

def getUsersInfo():
    return {
        'usersCount': len(list(usersCollection.find({'role': "USER"}))),
        'analystCount': len(list(usersCollection.find({'role': "ANALYST"}))),
        'adminCount': len(list(usersCollection.find({'role': "ADMIN"}))),
    }

def deleteUserDB(id):
    return usersCollection.delete_one({'_id': id}).deleted_count


def updateUserRoleDB(id, role):
    return usersCollection.update_one({'_id': id},
                               {"$set": {"role": role}}).modified_count

def updateUserName(id, username):
    return usersCollection.update_one({'_id': id},
                               {"$set": {"username": username}}).modified_count

def updateUserLogin(id, login):
    return usersCollection.update_one({'_id': id},
                               {"$set": {"login": login}}).modified_count

def updateUserPassword(id, password):
    return usersCollection.update_one({'_id': id},
                               {"$set": {"password": password}}).modified_count;