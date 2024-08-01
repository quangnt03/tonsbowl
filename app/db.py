import os 
from pymongo import MongoClient
from pymongo.errors import ConnectionFailure

cluster = MongoClient(os.environ['MONGO_URL'])
db = cluster[os.environ['DB_NAME']]
player_collection_name = os.environ['PLAYER_COLLECTION']
farm_collection_name = os.environ['FARM_COLLECTION']
referral_collection_name = os.environ['REFERRAL_COLLECTION']
collections = db.list_collection_names()

if player_collection_name not in collections:
    db.create_collection(player_collection_name)
if farm_collection_name not in collections:
    db.create_collection(farm_collection_name)
if referral_collection_name not in collections:
    db.create_collection(referral_collection_name)

db = cluster[os.environ['DB_NAME']]
user_collection = db[player_collection_name]
farm_collection = db[farm_collection_name]
referral_collection = db[referral_collection_name]

try:
    cluster.admin.command('ping')
    print('INFO:', '\t ', 'Connected to database')
except ConnectionFailure:
    print("Unable to connect database")
    exit(1)
except Exception:
    print("Server not available")
    exit(1)