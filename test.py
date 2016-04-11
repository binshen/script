# import re, config
# from pymongo import MongoClient
# 
# mongoClient = MongoClient(config.mongoDbUrl)
# db = mongoClient[config.mongoDbName]
# 
# restaurants = db.restaurants
# 
# data = {
#     'name': "Katz's DelicatesseN Catering",
#     'streetAddress': '205 E Houston St',
#     'state': 'NY',
#     'city': 'New York'
# }
# 
# restaurant = restaurants.find_one({ 
#         'name': re.compile(data['name'], re.IGNORECASE), 
#         'address': re.compile(data['streetAddress'], re.IGNORECASE), 
#         'state': re.compile(data['state'], re.IGNORECASE), 
#         'city': re.compile(data['city'], re.IGNORECASE) 
#     })
# print(restaurant) 

a = """
   [ 
        {
            "description" : null,
            "url" : "https://admin.delivery.com/item_images/485494_medium.gif",
            "id" : "E59",
            "type" : "image",
            "children" : [],
            "unique_id" : 59,
            "name" : "Cookies & Creme Cheesecake"
        }, 
        {
            "max_selection" : 1,
            "description" : "",
            "min_selection" : 1,
            "children" : [ 
                {
                    "description" : "",
                    "price" : 16,
                    "children" : [],
                    "id" : "E61",
                    "type" : "option",
                    "max_price" : 15,
                    "unique_id" : 61,
                    "name" : "6 Inch"
                }, 
                {
                    "description" : "",
                    "price" : 18.5,
                    "children" : [],
                    "id" : "E62",
                    "type" : "option",
                    "max_price" : 18.5,
                    "unique_id" : 62,
                    "name" : "Half 10 Inch"
                }, 
                {
                    "description" : "",
                    "price" : 36,
                    "children" : [],
                    "id" : "E63",
                    "type" : "option",
                    "max_price" : 35,
                    "unique_id" : 63,
                    "name" : "Whole 10 Inch"
                }
            ],
            "type" : "price group",
            "id" : "E60",
            "unique_id" : 60,
            "name" : "Pick One"
        }
    ]
"""

b = """
[ 
        {
            "apiKey" : "1569288",
            "customizations" : [ 
                {
                    "apiKey" : "10340649",
                    "type" : "DROPDOWN",
                    "name" : "",
                    "customizationChoices" : [ 
                        {
                            "count" : 1,
                            "price" : 0,
                            "apiKey" : "30053870",
                            "name" : "Chamomile Tea"
                        }, 
                        {
                            "count" : 1,
                            "price" : 0,
                            "apiKey" : "30053873",
                            "name" : "Peppermint Tea"
                        }, 
                        {
                            "count" : 1,
                            "price" : 0,
                            "apiKey" : "30053876",
                            "name" : "Earl Grey Tea"
                        }, 
                        {
                            "count" : 1,
                            "price" : 0,
                            "apiKey" : "30053881",
                            "name" : "English Breakfast Tea"
                        }, 
                        {
                            "count" : 1,
                            "price" : 0,
                            "apiKey" : "30053885",
                            "name" : "Green Tea"
                        }
                    ]
                }
            ],
            "name" : "Choose a tea:",
            "maxCount" : 2147483647
        }
    ]
"""

def fetch_menu_options(data):
    results = []
    if data:
        for option in data:
            if option.get('type', None) in ['price group', 'option group']:
                r = {}
                r['name'] = option.get('name')
                r['desc'] = option.get('description')
                r['min_selection'] = option.get('min_selection')
                r['max_selection'] = option.get('max_selection')
                options = []
                children = option.get('children')
                if children:
                    for child in children:
                        o = {}
                        o['name'] = child.get('name')
                        o['desc'] = child.get('description')
                        o['price'] = child.get('price')
                        o['max_price'] = child.get('max_price')
                        options.append(o)  
                r['options'] = options
                results.append(r)
    return results

# def fetch_menu_options(data):
#     results = []
#     if data:
#         for option in data:
#             r = {}
#             r['name'] = option.get('name')
#             r['desc'] = None
#             r['min_selection'] = None
#             r['max_selection'] = None
#             options = []
#             customizations = option.get('customizations')
#             if customizations:
#                 for customization in customizations:
#                     customizationChoices = customization.get('customizationChoices')
#                     if customizationChoices:
#                         for customizationChoice in customizationChoices:
#                             o = {}
#                             o['name'] = customizationChoice.get('name')
#                             o['desc'] = None
#                             o['price'] = customizationChoice.get('price')
#                             o['max_price'] = None
#                             options.append(o)
#             r['options'] = options
#             results.append(r)
#     return results

import json, pprint
data = json.loads(a)
pprint.pprint(fetch_menu_options(data)) 