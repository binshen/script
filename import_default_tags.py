import xlrd
from pymongo import MongoClient

mongoClient = MongoClient('mongodb://121.41.114.83:27017/')
db = mongoClient['consumer_db3']
tags = db.tags

if __name__ == '__main__':
    bk = xlrd.open_workbook('default_tags.xlsx')
    shxrange = range(bk.nsheets)
    sh = bk.sheet_by_index(0)
    nrows = sh.nrows
    ncols = sh.ncols
    for i in range(1,nrows):
        row_data = sh.row_values(i)
        tagName = row_data[0]
        tags.insert_one({ 'tagName': tagName, 'tagUser': 'default', 'upVote': None })
        