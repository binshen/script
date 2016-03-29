from pymongo import MongoClient, GEOSPHERE

mongoClient = MongoClient('mongodb://ksjs_user:passw0rd@ds019468.mlab.com:19468/consumer_db')
db = mongoClient['consumer_db']
restaurants = db.restaurants

restaurants.create_index([("loc",GEOSPHERE)])
