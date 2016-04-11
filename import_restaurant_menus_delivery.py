import requests, logging, config
from pymongo import MongoClient

logging.basicConfig(
    level=logging.WARN, 
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    filename='import_restaurant_menus_delivery.log', 
    filemode='w'
)

CLIENT_ID = 'YzIwMWRhMDI1NDAxNDBlNTUxYjdkNmEyOTYxNGVhNTBm'
URL_MERCHANT_MENU = 'https://api.delivery.com/merchant/%s/menu?client_id=%s'

mongoClient = MongoClient(config.mongoDbUrl)
db = mongoClient[config.mongoDbName]

restaurants = db.restaurants
dishes = db.dishes

def send_request(url):
    retries = 5
    for i in range(retries):
        try:
            return requests.get(url)
        except KeyError as e:
            if i < retries:
                logging.warn('----retry:' + i + ' - '+ url)
                continue
            else:
                logging.error('----error:' + url)
                raise e
        break

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

def import_restaurant_menu(restaurant_id, data, category):
    dish = {
        'partnerMenuId': {
            'delivery': {
                '_id': data['id']
            },
            'seamless': {
                '_id': None
            },
            'grubhub': {
                '_id': None
            }
        },
        "category": [ category ],
        "name": data['name'],
        "price": data['price'],
        "minQty": data['min_qty'],
        "maxQty": data['max_qty'],
        "restaurantId": restaurant_id,
        "customizeOptions": fetch_menu_options(data['children']),
        "listAdded": [],
        "listAddedCount": 0,
        "images": data['images'],
        "videos": [],
        "description": data['description'],
        "like": [],
        "likeCount": 0,
        'cpRating': {},
        'userRating': {}
    }
    return dishes.insert_one(dish).inserted_id

def parse_restaurant_menu(restaurant_id, data):
    dishes.delete_many({ 'restaurantId': restaurant_id })
    dishIds = []
    if 'menu' in data:
        menus = data['menu']
        for m1 in menus:
            if m1['type'] == 'menu':
                for m2 in m1['children']:
                    if m2['type'] == 'item':
                        dish_id = import_restaurant_menu(restaurant_id, m2, m1['name'])
                        dishIds.append(dish_id)
    if len(dishIds) > 0:
        restaurants.update({ "_id": restaurant_id }, { "$set": { "dishId": dishIds } })
    else:
        logging.warn(restaurant_id)

if __name__ == '__main__':
    for restaurant in restaurants.find():
        if 'partnerRestId' in restaurant and 'delivery' in restaurant['partnerRestId']:
            restaurant_id = restaurant['_id']
            marchant_id = restaurant['partnerRestId']['delivery']['_id']
            r = send_request(URL_MERCHANT_MENU % (marchant_id, CLIENT_ID))
            parse_restaurant_menu(restaurant_id, r.json())
        else:
            logging.error(restaurant)