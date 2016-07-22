import pymongo

class Database(object):
    URI = "mongodb://tarun:tarun@ds027165.mlab.com:27165/heroku_pxnl50q3"
    DATABASE =None

    @staticmethod
    def initialize():
        client=pymongo.MongoClient(Database.URI)
        Database.DATABASE=client['shows']

    @staticmethod
    def insert(collection,data):
        Database.DATABASE[collection].insert(data)

    @staticmethod
    def find(collection, query):
        return Database.DATABASE[collection].find(query)

    @staticmethod
    def find_one(collection, query):
        return Database.DATABASE[collection].find_one(query)

    @staticmethod
    def find_coloumn(collection,projection):
        return  Database.DATABASE[collection].find({},{projection:1, "_id":0})

    @staticmethod
    def remove_all(collection):
        Database.DATABASE[collection].remove({})

    @staticmethod
    def count_all(collection):
        return Database.DATABASE[collection].count({})


