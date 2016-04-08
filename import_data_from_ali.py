from pymongo import MongoClient

client1 = MongoClient('mongodb://121.41.114.83:27017/')
db1 = client1['consumer_db']

client2 = MongoClient('mongodb://b2cDevAdmin:devAdmin123@ds019860-a0.mlab.com:19860,ds019860-a1.mlab.com:19860/oh-b2c-mongo-dev2?replicaSet=rs-ds019860')
db2 = client2['oh-b2c-mongo-dev2']

collections = ['user_profiles', 'tags', 'lists', 'restaurants', 'dishes']

for collection in collections:
    for doc in db1[collection].find():
        db2[collection].insert_one(doc)