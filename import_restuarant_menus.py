import requests, logging
from pymongo import MongoClient

logging.basicConfig(
    level=logging.WARN, 
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    filename='import_restuarant_menus.log', 
    filemode='w'
)

CLIENT_ID = 'YzIwMWRhMDI1NDAxNDBlNTUxYjdkNmEyOTYxNGVhNTBm'
URL_MERCHANT_MENU = 'https://api.delivery.com/merchant/%s/menu?client_id=%s'

mongoClient = MongoClient('mongodb://121.41.114.83:27017/')
db = mongoClient['consumer_db3']
# mongoClient = MongoClient('mongodb://ksjs_user:passw0rd@ds019468.mlab.com:19468')
# db = mongoClient['consumer_db']

restuarants = db.restuarants
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

def import_restuarant_menu(restuarant_id, data, category):
    dish = {
        "category": [ category ],
        "name": data['name'],
        "price": data['price'],
        "restaurantId": restuarant_id,
        "listAdded": [],
        "images": data['images'],
        "videos": [],
        "description": data['description'],
        "like": [],
        "options": data['children']
    }
    return dishes.insert_one(dish).inserted_id

def parse_restuarant_menu(restuarant_id, data):
    dishes.delete_many({ 'restaurantId': restuarant_id })
    dishIds = []
    if 'menu' in data:
        menus = data['menu']
        for m1 in menus:
            if m1['type'] == 'menu':
                for m2 in m1['children']:
                    if m2['type'] == 'item':
                        dish_id = import_restuarant_menu(restuarant_id, m2, m1['name'])
                        dishIds.append(dish_id)
    if len(dishIds) > 0:
        restuarants.update({ "_id": restuarant_id }, { "$set": { "dishId": dishIds } })
    else:
        logging.warn(restuarant_id)

if __name__ == '__main__':
    for restuarant in restuarants.find():
        if 'extMerchantId' in restuarant:
            restuarant_id = restuarant['_id']
            marchant_id = restuarant['extMerchantId']
            r = send_request(URL_MERCHANT_MENU % (marchant_id, CLIENT_ID))
            parse_restuarant_menu(restuarant_id, r.json())
        else:
            logging.error(restuarant)