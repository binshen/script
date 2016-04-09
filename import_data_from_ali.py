import config
from pymongo import MongoClient

client1 = MongoClient('mongodb://121.41.114.83:27017/')
db1 = client1['consumer_db']

client2 = MongoClient(config.mongoDbUrl)
db2 = client2[config.mongoDbName]

collections = ['user_profiles', 'tags', 'lists', 'restaurants', 'dishes']

for collection in collections:
    for doc in db1[collection].find():
        db2[collection].insert_one(doc)