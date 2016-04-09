import config
from pymongo import MongoClient, GEOSPHERE

mongoClient = MongoClient(config.mongoDbUrl)
db = mongoClient[config.mongoDbName]
restaurants = db.restaurants

restaurants.create_index([("loc",GEOSPHERE)])
