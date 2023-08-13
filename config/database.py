from pymongo.mongo_client import MongoClient

client = MongoClient("mongodb+srv://ngamcode:N59wlZOe9cDpmt72@mjimagesdb.eguqvzs.mongodb.net/?retryWrites=true&w=majority")


db = client.db_mj_images

userCollection = db["user"]