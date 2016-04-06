import requests, logging
from pymongo import MongoClient

logging.basicConfig(
    level=logging.WARN, 
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    filename='import_restaurant_menus.log', 
    filemode='w'
)

URL_MERCHANT_MENU = 'https://api.eatstreet.com/publicapi/v1/restaurant/%s/menu?includeCustomizations=true'

mongoClient = MongoClient('mongodb://ksjs_user:passw0rd@ds019468.mlab.com:19468/consumer_db')
db = mongoClient['consumer_db']

restaurants = db.restaurants
dishes = db.dishes

def send_request(url):
    retries = 5
    for i in range(retries):
        try:
            return requests.get(url, headers={'X-Access-Token': '8248862ff81a39ff'})
        except KeyError as e:
            if i < retries:
                logging.warn('----retry:' + i + ' - '+ url)
                continue
            else:
                logging.error('----error:' + url)
                raise e

def import_restaurant_menu(restaurant_id, data, category, description):
    dish = {
        'partnerMenuId': {
            'delivery': {
                '_id': None
            },
            'seamless': {
                '_id': None
            },
            'grubhub': {
                '_id': None
            },
            'eatstreet': {
                '_id': data['apiKey']
            }           
        },
        "category": [ category ],
        "name": data['name'],
        "price": data['basePrice'],
        "minQty": None,
        "maxQty": None,
        "restaurantId": restaurant_id,
        "customizeOptions": data['customizationGroups'],
        "listAdded": [],
        "listAddedCount": 0,
        "images": [],
        "videos": [],
        "description": description,
        "like": [],
        "likeCount": 0,
        'cpRating': {},
        'userRating': {}
    }
    return dishes.insert_one(dish).inserted_id

def parse_restaurant_menu(restaurant_id, data):
    dishes.delete_many({ 'restaurantId': restaurant_id })
    dishIds = []
    for m1 in data:
        for m2 in m1['items']:
            dish_id = import_restaurant_menu(restaurant_id, m2, m1['name'], m1['description'])
            dishIds.append(dish_id)
    if len(dishIds) > 0:
        restaurants.update({ "_id": restaurant_id }, { "$set": { "dishId": dishIds } })
    else:
        logging.warn(restaurant_id)

if __name__ == '__main__':
    for restaurant in restaurants.find():
        if 'partnerRestId' in restaurant and 'eatstreet' in restaurant['partnerRestId']:
            if 'delivery' in restaurant['partnerRestId'] and restaurant['partnerRestId']['delivery']['_id']:
                continue
            restaurant_id = restaurant['_id']
            marchant_id = restaurant['partnerRestId']['eatstreet']['_id']
            r = send_request(URL_MERCHANT_MENU % (marchant_id))
            parse_restaurant_menu(restaurant_id, r.json())
        else:
            logging.error(restaurant)