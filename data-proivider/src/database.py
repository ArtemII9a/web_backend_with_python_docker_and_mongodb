from pymongo import MongoClient
from os import getenv
import uuid


class Database:
    def __init__(self):
        mongo_user = getenv("MONGO_INITDB_ROOT_USERNAME")
        mongo_password = getenv("MONGO_INITDB_ROOT_PASSWORD")
        mongo_location = getenv("APP_DB_LOCATION")
        client = MongoClient(f'mongodb://{mongo_user}:{mongo_password}@{mongo_location}/')
        self.db = client.data_provider

    def get_one(self, table, query):
        collection = self.db[f"{table}"]

        data = collection.find(query, {"_id": 0})
        
        output = []
        for item in data:
            output.append(item)
        return output

    def update_db(self, table, query, data):
        collection = self.db[f"{table}"]

        if query:
            if collection.find_one(query):
                collection.update_one(query, {'$set': data})
            else:
                data['id'] = str(uuid.uuid4())
                collection.insert_one(data)
                return data['id']
        else:
            data['id'] = str(uuid.uuid4())
            collection.insert_one(data)
            return data['id']

    def clear_all(self, table, query):
        collection = self.db[f"{table}"]
        item = collection.find_one(query)
        if item:
            collection.delete_one({"id": item["id"]})
