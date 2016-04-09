import re, config
from pymongo import MongoClient

mongoClient = MongoClient(config.mongoDbUrl)
db = mongoClient[config.mongoDbName]

restaurants = db.restaurants

data = {
    'name': "Katz's DelicatesseN Catering",
    'streetAddress': '205 E Houston St',
    'state': 'NY',
    'city': 'New York'
}

restaurant = restaurants.find_one({ 
        'name': re.compile(data['name'], re.IGNORECASE), 
        'address': re.compile(data['streetAddress'], re.IGNORECASE), 
        'state': re.compile(data['state'], re.IGNORECASE), 
        'city': re.compile(data['city'], re.IGNORECASE) 
    })
print(restaurant) 