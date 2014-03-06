# coding=utf-8
import pymongo
client = pymongo.MongoClient()
twitter = client['twitter']
tweets = twitter['tweets']
