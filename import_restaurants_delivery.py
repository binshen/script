import xlrd, requests, json, logging, config
from pymongo import MongoClient

logging.basicConfig(
    level=logging.WARN, 
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    filename='import_restaurants_delivery.log', 
    filemode='w'
)

CLIENT_ID = 'YzIwMWRhMDI1NDAxNDBlNTUxYjdkNmEyOTYxNGVhNTBm'
URL_POINT = 'https://api.delivery.com/merchant/search/delivery?client_id=%s&latitude=%s&longitude=%s'
URL_ADDRESS = 'https://api.delivery.com/merchant/search/delivery?client_id=%s&address=%s'
URL_MERCHANT = 'https://api.delivery.com/merchant/%s?client_id=%s'

mongoClient = MongoClient(config.mongoDbUrl)
db = mongoClient[config.mongoDbName]

restaurants = db.restaurants

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


def import_restaurant(marchant_id, data):
    if 'merchant' in data:
        merchant = data['merchant']
        merchant_id = merchant['id']
        restaurant = restaurants.find_one({ 'partnerRestId.delivery._id': str(merchant_id) })
        if restaurant:
            restaurants.update({ '_id': restaurant['_id'] }, { '$set': {
                'cuisines': merchant['summary']['cuisines'],
                'name': merchant['summary']['name'],
                'address': merchant['location']['street'],
                'city': merchant['location']['city'],
                'state': merchant['location']['state'],
                'zip': merchant['location']['zip'],
                'activationDate': merchant['summary']['activation_date'],
                'loc': {
                    "type": "Point",
                    "coordinates": [ 
                        merchant['location']['longitude'], 
                        merchant['location']['latitude']
                    ]
                },
                'latitude': merchant['location']['latitude'],
                'longitude': merchant['location']['longitude'],
                'contactInfo': {
                    'email' :[],
                    'phone': [merchant['summary']['phone']]
                },
                'logo': {
                    'thumbSize': None,
                    'midSize': merchant['summary']['merchant_logo'],
                    'rawSize': merchant['summary']['merchant_logo_raw']
                },
                'description': merchant['summary']['description'],
                'note': merchant['summary']['notes'],
                'priceRange': merchant['summary']['price_rating'],
                'images': data['images'] if 'images' in data else [],
                'starRating': merchant['summary']['star_ratings'],
                'pickUp': merchant['ordering']['availability']['pickup_supported'],
                'delivery': merchant['ordering']['availability']['delivery_supported'],
                'minimumForDelievery': merchant['ordering']['minimum']['delivery']['lowest'],
                'startPickUpTime': merchant['ordering']['availability']['next_pickup_time'],
                'startDeliveryTime': merchant['ordering']['availability']['next_delivery_time'],
                'lastPickUpTime': merchant['ordering']['availability']['last_pickup_time'],
                'lastDeliveryTime': merchant['ordering']['availability']['last_delivery_time'],
                'pickUpEstimate': merchant['ordering']['availability']['pickup_estimate'],
                'deliveryEstimate': merchant['ordering']['availability']['delivery_estimate']
            }})
        else:
            restaurants.insert_one({
                'partnerRestId': {
                    'delivery': {
                        '_id': merchant['id'],
                        'url': merchant['summary']['url']['complete']
                    },
                    'seamless': {
                        '_id': None,
                        'url': None
                    },
                    'grubhub': {
                        '_id': None,
                        'url': None
                    },
                    'eatstreet': {
                        '_id': None,
                        'url': None
                    }
                },
                'cuisines': merchant['summary']['cuisines'],
                'dishId': [],
                'name': merchant['summary']['name'],
                'address': merchant['location']['street'],
                'city': merchant['location']['city'],
                'state': merchant['location']['state'],
                'zip': merchant['location']['zip'],
                'activationDate': merchant['summary']['activation_date'],
                'loc': {
                    "type": "Point",
                    "coordinates": [ 
                        merchant['location']['longitude'], 
                        merchant['location']['latitude']
                    ]
                },
                'latitude': merchant['location']['latitude'],
                'longitude': merchant['location']['longitude'],
                'contactInfo': {
                    'email' :[],
                    'phone': [merchant['summary']['phone']]
                },
                'logo': {
                    'thumbSize': None,
                    'midSize': merchant['summary']['merchant_logo'],
                    'rawSize': merchant['summary']['merchant_logo_raw']
                },
                'description': merchant['summary']['description'],
                'note': merchant['summary']['notes'],
                'priceRange': merchant['summary']['price_rating'],
                'images': data['images'] if 'images' in data else [],
                'videos': [],
                'like': [],
                'starRating': merchant['summary']['star_ratings'],
                'cpRating': {},
                'userRating': {},
                'pickUp': merchant['ordering']['availability']['pickup_supported'],
                'delivery': merchant['ordering']['availability']['delivery_supported'],
                'minimumForDelievery': merchant['ordering']['minimum']['delivery']['lowest'],
                'startPickUpTime': merchant['ordering']['availability']['next_pickup_time'],
                'startDeliveryTime': merchant['ordering']['availability']['next_delivery_time'],
                'lastPickUpTime': merchant['ordering']['availability']['last_pickup_time'],
                'lastDeliveryTime': merchant['ordering']['availability']['last_delivery_time'],
                'pickUpEstimate': merchant['ordering']['availability']['pickup_estimate'],
                'deliveryEstimate': merchant['ordering']['availability']['delivery_estimate']
            })
    else:
        logging.warn('----------id:' + marchant_id + ' data:' + json.dumps(data))

marchant_ids = []
def parse_marchant(marchants):
    for marchant in marchants:
        marchant_id = marchant['id']
        if not marchant_id in marchant_ids:
            marchant_ids.append(marchant_id)
            r = send_request(URL_MERCHANT % (marchant_id, CLIENT_ID))
            import_restaurant(marchant_id, r.json())

if __name__ == '__main__':
    bk = xlrd.open_workbook('points.xlsx')
    shxrange = range(bk.nsheets)
    sh = bk.sheet_by_index(0)
    nrows = sh.nrows
    ncols = sh.ncols
    for i in range(1,nrows):
        row_data = sh.row_values(i)
        r = send_request(URL_POINT % (CLIENT_ID, row_data[0], row_data[1]))
        response = r.json()
        search_address = response.get('search_address')
        if search_address:
            parse_marchant(response.get('merchants'))
        else:
            addresses = response.get('addresses')
            if addresses:
                for address in addresses:
                    addr = address.get('street') + ' ' + address.get('zip')
                    r = send_request(URL_ADDRESS % (CLIENT_ID, addr))
                    response = r.json()
                    search_address = response.get('search_address')
                    if search_address:
                        parse_marchant(response.get('merchants'))