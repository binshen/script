from pymongo import MongoClient, GEOSPHERE

mongoClient = MongoClient('mongodb://b2cDevAdmin:devAdmin123@ds019860-a0.mlab.com:19860,ds019860-a1.mlab.com:19860/oh-b2c-mongo-dev2?replicaSet=rs-ds019860')
db = mongoClient['oh-b2c-mongo-dev2']
restaurants = db.restaurants

restaurants.create_index([("loc",GEOSPHERE)])
