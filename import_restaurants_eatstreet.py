import xlrd, requests, re, logging, config
from pymongo import MongoClient

logging.basicConfig(
    level=logging.WARN, 
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    filename='import_restaurants_eat.log', 
    filemode='w'
)

URL_POINT = 'https://api.eatstreet.com/publicapi/v1/restaurant/search?latitude=%s&longitude=%s&method=both'

mongoClient = MongoClient(config.mongoDbUrl)
db = mongoClient[config.mongoDbName]
restaurants = db.restaurants

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

def import_restaurant(data):
    
    restaurant = restaurants.find_one({ 
        'name': re.compile(data['name'], re.IGNORECASE), 
        'address': re.compile(data['streetAddress'], re.IGNORECASE), 
        'state': re.compile(data['state'], re.IGNORECASE), 
        'city': re.compile(data['city'], re.IGNORECASE) 
    })
    if restaurant:
        partnerRestId = restaurant['partnerRestId']
        partnerRestId['eatstreet'] = {
            '_id': data['apiKey'],
            'url': None
        }
        restaurants.update({ '_id': restaurant['_id'] }, { '$set': {
            'partnerRestId': partnerRestId,
        }})
    else:
        restaurants.insert_one({
            'partnerRestId': {
                'delivery': {
                    '_id': None,
                    'url': None
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
                    '_id': data['apiKey'],
                    'url': None
                }
            },
            'cuisines': data['foodTypes'],
            'dishId': [],
            'name': data['name'],
            'address': data['streetAddress'],
            'city': data['city'],
            'state': data['state'],
            'zip': data['zip'],
            'activationDate': None,
            'loc': {
                "type": "Point",
                "coordinates": [ 
                    data['longitude'], 
                    data['latitude']
                ]
            },
            'latitude': data['latitude'],
            'longitude': data['longitude'],
            'contactInfo': {
                'email' :[],
                'phone': []
            },
            'logo': {
                'thumbSize': data['logoUrl'],
                'midSize': None,
                'rawSize': None
            },
            'description': None,
            'note': None,
            'priceRange': None,
            'images': [],
            'videos': [],
            'like': [],
            'starRating': None,
            'cpRating': {},
            'userRating': {},
            'pickUp': data['offersPickup'],
            'delivery': data['offersDelivery'],
            'minimumForDelievery': data['minFreeDelivery'],
            'startPickUpTime': None,
            'startDeliveryTime': None,
            'lastPickUpTime': None,
            'lastDeliveryTime': None,
            'pickUpEstimate': None,
            'deliveryEstimate': None
        })

marchant_ids = []
def parse_restaurant(restaurants):
    for restaurant in restaurants:
        marchant_id = restaurant['apiKey']
        if not marchant_id in marchant_ids:
            marchant_ids.append(marchant_id)
            import_restaurant(restaurant)

if __name__ == '__main__':
    bk = xlrd.open_workbook('points.xlsx')
    shxrange = range(bk.nsheets)
    sh = bk.sheet_by_index(0)
    nrows = sh.nrows
    ncols = sh.ncols
    for i in range(1,nrows):
        row_data = sh.row_values(i)
        r = send_request(URL_POINT % (row_data[0], row_data[1]))
        response = r.json()
        parse_restaurant(response.get('restaurants'))