from pymongo import MongoClient

client = MongoClient('localhost', 27017)
db = client.api

## 코딩 할 준비 ##

gu = db.weather.find_one({'2단계': })
