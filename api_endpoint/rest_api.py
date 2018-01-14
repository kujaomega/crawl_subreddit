import pymongo
from bson.json_util import dumps
import json


def get_top_10_by_points(event, context):
    working_collection = get_working_collection()
    found_subreddits = get_find_subreddits(event, working_collection)
    result = found_subreddits.sort("punctuation", pymongo.DESCENDING).limit(10)
    return cursor_to_json(result)


def get_top_10_by_num_comments(event, context):
    working_collection = get_working_collection()
    found_subreddits = get_find_subreddits(event, working_collection)
    result = found_subreddits.sort("num_comments", pymongo.DESCENDING).limit(10)
    return cursor_to_json(result)


def get_top_10_submitters(event, context):
    working_collection = get_working_collection()
    pipe = [{"$group":
            {"_id": {"author": "$author"},
             "count": {"$sum": 1}}},
            {"$sort": {"count": -1}},
            {"$limit": 10}]
    found_subreddits = working_collection.aggregate(pipeline=pipe)
    return cursor_to_json(found_subreddits)


def get_find_subreddits(event, working_collection):
    if event['query']:
        if event['query']['rank']:
            if event['query']['rank'] == "all":
                result = working_collection.find()
            elif event['query']['rank'] == "discussion":
                result = working_collection.find({'external_article': False})
            elif event['query']['rank'] == "external":
                result = working_collection.find({'external_article': True})
            else:
                result = working_collection.find()
            return result
    result = working_collection.find()
    return result


def cursor_to_json(cursor):
    json_string = dumps(cursor)
    json_string = json.loads(json_string)
    return json_string


def get_working_collection():
    with open('mongo_db.json') as data_file:
        data_item = json.load(data_file)
    client = pymongo.MongoClient(data_item["mongo_url"])
    test_database = client.get_database(data_item["mongo_database"])
    working_collection = test_database.get_collection(data_item["mongo_collection"])
    return working_collection
