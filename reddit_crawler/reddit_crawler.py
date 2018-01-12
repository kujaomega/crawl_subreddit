from reddit_api import RedditApi
from pymongo import MongoClient
import logging
import json


def lambda_handler(event, context):
    crawl_api_endpoint()


def crawl_api_endpoint(pages_limit=1):
    reddit_api = RedditApi()
    pages_limit = pages_limit
    last_subreddit_name = None
    all_subreddits = []
    logging.basicConfig()
    logger = logging.getLogger('database')
    logger.setLevel(logging.NOTSET)
    for i in range(pages_limit):
        discussions = reddit_api.get_subreddits(last_subreddit_name)
        response_data = discussions['data']['children']
        for subreddit in response_data:
            created_subreddit = get_subreddit_data(subreddit)
            last_subreddit_name = created_subreddit['name']
            all_subreddits.append(created_subreddit)
    working_collection = get_working_collection()
    subreddits_to_create, subreddits_to_update = check_existing_subreddits(working_collection, all_subreddits, logger)
    create_subreddits(working_collection, subreddits_to_create, logger)
    update_subreddits(working_collection, subreddits_to_update, logger)


def get_subreddit_data(subreddit):
    created_subreddit = dict()
    created_subreddit['name'] = subreddit['data']['name']
    created_subreddit['title'] = subreddit['data']['title']
    created_subreddit['external_url'] = subreddit['data']['url']
    created_subreddit['discussion_url'] = subreddit['data']['permalink']
    created_subreddit['author'] = subreddit['data']['author']
    created_subreddit['punctuation'] = subreddit['data']['ups']
    created_subreddit['created'] = subreddit['data']['created']
    created_subreddit['num_comments'] = subreddit['data']['num_comments']
    created_subreddit['external_article'] = not subreddit['data']['permalink'] in subreddit['data']['url']
    return created_subreddit


def get_working_collection():
    with open('mongo_db.json') as data_file:
        data_item = json.load(data_file)
    client = MongoClient(data_item["mongo_client"])
    test_database = client.get_database(data_item["mongo_database"])
    working_collection = test_database.get_collection(data_item["mongo_collection"])
    return working_collection


def check_existing_subreddits(mongo_collection, subreddits, logger):
    subreddits_to_create = []
    subreddits_to_update = []
    for subreddit in subreddits:
        subreddit_name = subreddit['name']
        subreddits_to_create.append({'name': subreddit_name})
    existing_subreddits = mongo_collection.find({"$or": subreddits_to_create}).limit(0)
    subreddits_to_create = subreddits[:]
    for existing_subreddit in existing_subreddits:
        for subreddit in subreddits:
            if subreddit['name'] == existing_subreddit['name']:
                logger.info('subreddit %s is duplicated' % subreddit['name'])
                subreddits_to_update.append(subreddit)
                subreddits_to_create.remove(subreddit)
    return subreddits_to_create, subreddits_to_update


def create_subreddits(mongo_collection, body, logger):
    if len(body) > 0:
        result_insert = mongo_collection.insert(body)
        logger.info('result_insert', result_insert)


def update_subreddits(mongo_collection, body, logger):
    if len(body) > 0:
        bulkop = mongo_collection.initialize_ordered_bulk_op()
        for subreddit in body:
            bulkop.find({'name': subreddit['name']}).upsert().update({'$set': subreddit})
            logger.info('update_operation')
        bulkop.execute()


if __name__ == "__main__":
    first_n_pages = 50000
    crawl_api_endpoint(first_n_pages)
