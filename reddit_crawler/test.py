from reddit_api import RedditApi


def main():
    test_api_endpoint()


def test_api_endpoint():
    reddit_api = RedditApi()
    base_url = "https://www.reddit.com"
    pages_limit = 4
    last_subreddit_name = None
    for i in range(pages_limit):

        discussions = reddit_api.get_subreddits(last_subreddit_name)
        response_data = discussions['data']['children']
        for subreddit in response_data:
            name = subreddit['data']['name']
            title = subreddit['data']['title']
            external_url = subreddit['data']['url']
            discussion_url = subreddit['data']['permalink']
            author = subreddit['data']['author']
            punctuation = subreddit['data']['ups']
            created = subreddit['data']['created']
            num_comments = subreddit['data']['num_comments']
            last_subreddit_name = name

            print("name: %s title:%s\n" % (name, title))


main()
