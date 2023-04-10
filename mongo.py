from datetime import date
from pymongo import MongoClient

cluster = MongoClient('mongodb+srv://fortelra19:fortelra19@devby.4yo2tlq.mongodb.net/?retryWrites=true&w=majority')
db = cluster['DB_DEVBY']
collection = db['COLLECTION_DEVBY']

def addToDataBase(data):
    collection.insert_one({
        'date': str(date.today()),
        'data': data,
    })