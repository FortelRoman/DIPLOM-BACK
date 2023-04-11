from datetime import date
from pymongo import MongoClient
import uuid

cluster = MongoClient('mongodb+srv://fortelra19:fortelra19@devby.4yo2tlq.mongodb.net/?retryWrites=true&w=majority')
db = cluster['DB_DEVBY']
collection = db['COLLECTION_DEVBY']

def addItem(data):
    collection.insert_one({
        '_id': str(uuid.uuid4()),
        'date': str(date.today()),
        'vacancies': data,
    })


def getList():
    return collection.find()

def deleteItem(id):
    collection.delete_one({'_id': id})

def getItem(id):
    return collection.find_one({'_id': id})['vacancies']

