Steps to import data into mongodb (mongolab)

1. Update DB setting in config.py

2. Pull restaurant data from delivery using the following command:
   python import_restaurants_delivery.py
   
3. Pull menu data from delivery using the following command:
   python import_restaurant_menus_delivery.py
   
4. Pull restaurant data from eatstreet using the following command:
   python import_restaurants_eatstreet.py
   
5. Pull menu data from eatstreet using the following command:
   python import_restaurant_menus_eatstreet.py
   
6. Add GeoSphere index to restaurant collection using the following command:
   python create_indexes.py