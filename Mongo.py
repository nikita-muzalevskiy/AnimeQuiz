from pymongo import MongoClient

class MongoDB(object):
    def __init__(self, host: str = 'localhost',
                 port: int = 27017,
                 db_name: str = 'Anime_Tests',
                 collection: str = 'user_condition'):
        self._client = MongoClient(f'mongodb://{host}:{port}')
        self._collection = self._client[db_name][collection]

    def findUser(self, user: str):
        try:
            if self._collection.find_one({"user": user}) == None:
                return 0
            else:
                return 1
        except Exception as ex:
            print("[create_user] Some problem...")
            print(ex)

    def getDocument(self, user: str):
        try:
            if self._collection.find_one({"user": user}) == None:
                print('Не нашли пользователя')
            else:
                return self._collection.find_one({"user": user})
        except Exception as ex:
            print("[create_user] Some problem...")
            print(ex)

    def createUser(self, user: str):
        try:
            if self._collection.find_one({"user": user}) == None:
                self._collection.insert_one({"user": user})
            else:
                print(f"User: {user} in collection")
        except Exception as ex:
            print("[createUser] Some problem...")
            print(ex)

    def updateUser(self, user: str, params: dict):
        try:
            self._collection.replace_one({"user": user}, params)
        except Exception as ex:
            print("[updateUser] Some problem...")
            print(ex)

    def updateOne(self, user: str, params: dict):
        try:
            self._collection.update_one({"user": user}, { "$set": params})
        except Exception as ex:
            print("[updateOne] Some problem...")
            print(ex)