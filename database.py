from pymongo import MongoClient, ASCENDING


client = MongoClient("mongodb://localhost:27017/")
db = client['blogdb']
users = db['users']
users.create_index([('username', ASCENDING)], unique=True)

blogs = db['blogs']
