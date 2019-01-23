from pymongo import MongoClient

client = MongoClient('mongodb://yahoo:yah00!@ds157223.mlab.com:57223/yahoo-scraper')
# client = pymongo.MongoClient('MONGOALCHEMY_CONNECTION_STRING')

mdb = client['yahoo-scraper']
print("mdb.name == " + mdb.name)
# data = mdb.name
collection = mdb.totals
print("collection == " + collection.name)
# print("data: ")
for x in collection.find():
    print(x)
