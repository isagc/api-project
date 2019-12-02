#!/usr/local/bin/python3
from pymongo import MongoClient
import getpass
import json
import os
from dotenv import load_dotenv
load_dotenv()

#Get Password
connection = os.getenv("MONGO_ATLAS")
#Connect to DB
client = MongoClient(connection)
def connectCollection(database, collection):
    db = client[database]
    coll = db[collection]
    return db, coll

db, coll = connectCollection('api-project','api-project')

with open('./chats.json') as f:
    chats_json = json.load(f)

if coll == 0:
    coll.insert_many(chats_json)