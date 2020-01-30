"""
@ProjectName: yangshipin-Crawler
@FileName: db.py
@Author: GENGSHUQIANG
@Date: 2020/1/30
"""
from pymongo import MongoClient

client = MongoClient('mongodb://ip:port/admin')
db = client['nCov2019']
db.authenticate(name='userName', password='******', mechanism='SCRAM-SHA-1')


class DB:
    def __init__(self):
        self.db = db

    def insert(self, collection, data):
        self.db[collection].insert(data)

    def update(self, collection, data):
        self.db[collection].update(data)

    def find_one(self, collection, data=None):
        return self.db[collection].find_one(data)