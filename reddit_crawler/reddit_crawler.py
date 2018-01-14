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

    logging.basicConfig()
    logger = logging.getLogger('database')
    logger.setLevel(logging.NOTSET)
    logger2 = logging.getLogger('crawler')
    logger2.setLevel(logging.NOTSET)
    working_collection = get_working_collection()
    for i in range(pages_limit):
        try:
            discussions = reddit_api.get_subreddits(last_subreddit_name)
            response_data = discussions['data']['children']
            all_subreddits = []
            for subreddit in response_data:
                created_subreddit = get_subreddit_data(subreddit, reddit_api, logger2)
                last_subreddit_name = created_subreddit['name']
                all_subreddits.append(created_subreddit)
            subreddits_to_create, subreddits_to_update = check_existing_subreddits(working_collection, all_subreddits,
                                                                                   logger)
            create_subreddits(working_collection, subreddits_to_create, logger)
            update_subreddits(working_collection, subreddits_to_update, logger)
        except Exception:
            logger2.exception("Call error last_subreddit_name : %s" % last_subreddit_name)


def get_subreddit_data(subreddit, reddit_api, logger):
    created_subreddit = dict()
    try:
        created_subreddit['name'] = subreddit['data']['name']
        created_subreddit['title'] = subreddit['data']['title']
        created_subreddit['external_url'] = subreddit['data']['url']
        created_subreddit['discussion_url'] = subreddit['data']['permalink']
        created_subreddit['author'] = subreddit['data']['author']
        created_subreddit['punctuation'] = subreddit['data']['score']
        created_subreddit['created'] = subreddit['data']['created']
        created_subreddit['num_comments'] = subreddit['data']['num_comments']
        created_subreddit['external_article'] = not subreddit['data']['permalink'] in subreddit['data']['url']
        created_subreddit['comments'] = get_comments_info(reddit_api, subreddit['data']['permalink'], logger)
    except KeyError:
        logger.exception("Key error in subreddit with data : %s" % subreddit['data'])

    return created_subreddit


def get_comments_info(reddit_api, url, logger):
    comments_url = url[:-1] + ".json"
    comments_data_from_url = reddit_api.get_comments_url(comments_url)
    comments = get_replies(comments_data_from_url[1], logger)
    return comments


def get_replies(comment, logger):
    comments = []
    for comment in comment['data']['children']:
        try:
            comment_data_to_save = dict()
            if comment['data']:
                comment_data_to_save['body'] = comment['data']['body']
                comment_data_to_save['author'] = comment['data']['author']
                comment_data_to_save['punctuation'] = comment['data']['score']
                comments.append(comment_data_to_save)
                if comment['data']['replies'] != "":
                    replies_comments = get_replies(comment['data']['replies'], logger)
                    comments.extend(replies_comments)
        except Exception:
            logger.exception("Error in replies with data : %s" % comment['data']['children'])
    return comments


def get_working_collection():
    with open('mongo_db.json') as data_file:
        data_item = json.load(data_file)
    client = MongoClient(data_item["mongo_url"])
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
    if existing_subreddits:
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
    first_n_pages = 50
    crawl_api_endpoint(first_n_pages)
