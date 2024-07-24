import os 
from pymongo import MongoClient
from pymongo.errors import ConnectionFailure


cluster = MongoClient(os.environ['MONGO_URL'])
db = cluster[os.environ['DB_NAME']]
user_collection = db[os.environ['PLAYER_COLLECTION']]

try:
    cluster.admin.command('ping')
    print('INFO:', '\t', 'connected to database')
except ConnectionFailure:
    print("Unable to connect database")
except Exception:
    print("Server not available")