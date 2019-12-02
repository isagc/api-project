
from bottle import route, run, get, post, request
import populate as p
import json
import random
import bson
from bson.json_util import dumps
import requests
import nltk 
from nltk.sentiment.vader import SentimentIntensityAnalyzer
from functools import reduce

db, coll = p.connectCollection('api-project','api-project')

# Get everything
@get("/")
def index():
    return dumps(coll.find())  

# Get all usernames and show only 'userName' field
@get("/username")
def username():
    return dumps(coll.find({},{"userName":1}))

# Get all chats and show only 'idChat' field
@get("/chats")
def chats():
    return dumps(coll.find({}, {"idChat":1}))

# Get all messages from `chat_id`
@get("/chat/<chat_id>")
def oneChat(chat_id):
    data = list(coll.find({"idChat": int(chat_id)}, {"_id": 0}))
    return {
        "messages": [[d['idMessage'], int(d['idUser']), d["text"]] for d in data]
    }

# Create a user and save into DB
@post("/user/create")
def createUser():
    new_id = coll.distinct("idUser")[-1] + 1
    all_names = coll.distinct("userName")
    name = str(request.forms.get("userName"))
    print(name)
    if name in all_names:
        return "Username already exists in database. Try a different one :)"
    else:
        new_user = {
            "idUser" : new_id,
            "userName" : name
        } 
        print(new_user)
        coll.insert_one(new_user)
        return f"new_id: {new_id}"

# Create a conversation to load messages
@post("/chat/create")
def createChat():
    new_idChat = coll.distinct("idChat")[-1] + 1
    all_ids = coll.distinct("idUser")
    user_id = list(request.forms.getall("idUser"))
    print(user_id)
    info_grupo = []
    for u in user_id:
        user = {}
        user_info = coll.find({"idUser":int(u)}, {"userName":1})
        print(user_info)
        user['idUser'] = u
        user['userName'] = user_info[0]['userName']
        user['idChat'] = new_idChat
        print(user)
        info_grupo.append(user)
    coll.insert_many(info_grupo)
    return f"new_idChat: {new_idChat}"

# Add a message to the conversation
@post("/chat/<chat_id>/addmessage")
def addMessage(chat_id):
    new_idMessage = max(coll.distinct("idMessage")) + 1
    idUser = str(request.forms.get("idUser"))
    message = str(request.forms.get("text"))
    fields = list(coll.find({"idUser":idUser},{"userName":1, "idUser":1, "_id":0,"idChat":1}))
    print(fields)
    name = fields[0]["userName"]
    for f in fields:
        if f["userName"] == name:
            new_idUser = f["idUser"]
        else:
            name = name
    new_message = {
        "idUser" : idUser,
        "userName" : name,
        "idChat" : int(chat_id),
        "idMessage" : new_idMessage,
        "datetime" : datetime.datetime.utcnow(),
        "text" : message
    }
    print(new_message)
    new_user = {
        "idUser" : new_idUser,
        "userName" : name
    }
    print(new_user)
    coll.insert_one(new_message)
    coll.insert_one(new_user)
    return f"idMessage: {new_idMessage}"

# Analyze messages from `chat_id`
@get('/chat/<chat_id>/sentiment')
def getSentiments(chat_id):
    messages = oneChat(chat_id)
    sid = SentimentIntensityAnalyzer()
    sentiments = []
    for m in list(messages['messages']):
        info_sentiment = {}
        info_sentiment['MessageID'] = m[0]
        info_sentiment['UserID'] = m[1]
        info_sentiment['Message'] = m[2]
        info_sentiment['Sentiment'] = sid.polarity_scores(m[2])
        sentiments.append(info_sentiment)
    print(sentiments)
    
    #compound = [e['Sentiment']['compound'] for e in sentiments]
    #avg_compound = reduce((lambda x,y : x+y), compound)

    for m in list(messages['messages']):
        coll.update_one({"idMessage":m[0]}, {"$set": {"sentiment":sentiments}})
    return {
        "sentiment" : sentiments,
        "compounds" : compound,
        "average compounds" : avg_compound
    }

run(host='0.0.0.0', port=8080)

