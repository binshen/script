import xlrd, requests, json, logging
from pymongo import MongoClient

logging.basicConfig(
    level=logging.WARN, 
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    filename='import_restuarants.log', 
    filemode='w'
)

CLIENT_ID = 'YzIwMWRhMDI1NDAxNDBlNTUxYjdkNmEyOTYxNGVhNTBm'
URL_POINT = 'https://api.delivery.com/merchant/search/delivery?client_id=%s&latitude=%s&longitude=%s'
URL_ADDRESS = 'https://api.delivery.com/merchant/search/delivery?client_id=%s&address=%s'
URL_MERCHANT = 'https://api.delivery.com/merchant/%s?client_id=%s'

mongoClient = MongoClient('mongodb://121.41.114.83:27017/')
db = mongoClient['consumer_db3']
# mongoClient = MongoClient('mongodb://ksjs_user:passw0rd@ds019468.mlab.com:19468')
# db = mongoClient['consumer_db']

restuarants = db.restuarants

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


def import_restuarant(marchant_id, data):
    if 'merchant' in data:
        merchant = data['merchant']
        merchant_id = merchant['id']
        restuarant = restuarants.find_one({ 'extMerchantId': str(merchant_id) })
        if restuarant:
            restuarants.update({ '_id': restuarant['_id'] }, { '$set': {
                'name': merchant['summary']['name'],
                'address': merchant['location']['street'],
                'city': merchant['location']['city'],
                'state': merchant['location']['state'],
                'loc': {
                    "type" : "Point",
                    "coordinates" : [ 
                        merchant['location']['longitude'], 
                        merchant['location']['latitude']
                    ]
                },
                'latitude': merchant['location']['latitude'],
                'longitude': merchant['location']['longitude'],
                'logo': merchant['summary']['merchant_logo'],
                'description': merchant['summary']['description'],
                'priceRange': merchant['summary']['price_rating'],
                'images': data['images'] if 'images' in data else [],
                'zip': merchant['location']['zip'],
                'phone': merchant['summary']['phone'],
                'starRating': merchant['summary']['star_ratings'],
                'cuisines': merchant['summary']['cuisines'],
                'url': merchant['summary']['url']['complete']
            }})
        else:
            restuarants.insert_one({
                'dishId': [],
                'name': merchant['summary']['name'],
                'address': merchant['location']['street'],
                'city': merchant['location']['city'],
                'state': merchant['location']['state'],
                'loc': {
                    "type" : "Point",
                    "coordinates" : [ 
                        merchant['location']['longitude'], 
                        merchant['location']['latitude']
                    ]
                },
                'latitude': merchant['location']['latitude'],
                'longitude': merchant['location']['longitude'],
                'contactInfo': [],
                'logo': merchant['summary']['merchant_logo'],
                'description': merchant['summary']['description'],
                'priceRange': merchant['summary']['price_rating'],
                'images': data['images'] if 'images' in data else [],
                'videos': [],
                'like': [],
                'cpRating': {},
                'userRating': {},
                'extMerchantId': merchant['id'],
                'zip': merchant['location']['zip'],
                'phone': merchant['summary']['phone'],
                'starRating': merchant['summary']['star_ratings'],
                'cuisines': merchant['summary']['cuisines'],
                'url': merchant['summary']['url']['complete']
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
            import_restuarant(marchant_id, r.json())

if __name__ == '__main__':
    bk = xlrd.open_workbook('points.xlsx')
    shxrange = range(bk.nsheets)
    sh = bk.sheet_by_index(0)
    nrows = sh.nrows
    ncols = sh.ncols
    cell_value = sh.cell_value(1,1)
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