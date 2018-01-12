import requests
import requests.auth
import logging
import time


class RedditApi:

    def __init__(self, base_url="https://www.reddit.com", client_id="z1c3vPJqtNGq2Q",
                 secret="sjYln1SRY5AX2sywTFHwyLOqKUw", username="testBlueliv", password="P@@ssw0rd",
                 get_token_endpoint="/api/v1/access_token",
                 authenticated_url="https://oauth.reddit.com", log_level=logging.NOTSET, http_timeout=60,
                 initial_rate_limit=600, initial_reset_rate_limit=600):
        self.log_level = log_level
        self.http_timeout = http_timeout

        client_auth = requests.auth.HTTPBasicAuth(client_id, secret)
        post_data = {"grant_type": "password",
                     "username": username, "password": password, "duration": "permanent"}
        headers = {"User-Agent": "ChangeMeClient/0.1 by YourUsername"}
        status_code, response = self.post(base_url + get_token_endpoint, headers, client_auth, post_data)
        self.token = response["token_type"] + " " + response["access_token"]
        self.authenticated_headers = {"Authorization": self.token,
                                      "Content-Type": "application/json",
                                      "User-Agent": "ChangeMeClient/0.1 by YourUsername"}
        self.authenticated_url = authenticated_url
        self.rate_limit = initial_rate_limit
        self.reset_rate_limit = initial_reset_rate_limit

    def get_me(self):
        endpoint = "/api/v1/me"
        response = self.get(self.authenticated_url + endpoint, headers=self.authenticated_headers)
        return response

    def get_subreddits(self, last_subreddit=None):
        endpoint = "/r/Python/new.json"
        queryparams = "?sort=new&count=25"
        if last_subreddit is not None:
            queryparams = queryparams + "&after=" + last_subreddit
        status_code, response = self.get(self.authenticated_url + endpoint + queryparams, headers=self.authenticated_headers)
        return response

    def get_comments_url(self, url_path):
        status_code, response = self.get(self.authenticated_url + url_path, headers=self.authenticated_headers)
        return response

    def get(self, url, headers):
        logger = logging.getLogger('get')
        logger.setLevel(self.log_level)
        response = None
        status_code = None
        if self.rate_limit <= 0:
            time.sleep(self.reset_rate_limit)
        try:
            r = requests.get(url, verify=True, headers=headers, timeout=self.http_timeout)
            self.rate_limit = float(r.headers['x-ratelimit-remaining'])
            self.reset_rate_limit = float(r.headers['x-ratelimit-reset'])
            status_code = r.status_code
            r.raise_for_status()
            response = r.json()
        except Exception:
            logger.exception("Call error url : %s" % url)

        return (status_code, response)

    def post(self, url, headers, client_auth, post_data):
        logger = logging.getLogger('post')
        logger.setLevel(self.log_level)
        response = None
        status_code = None
        try:
            r = requests.post(url, verify=True, auth=client_auth, data=post_data,
                              headers=headers, timeout=self.http_timeout)
            status_code = r.status_code
            r.raise_for_status()
            response = r.json()
        except Exception:
            logger.exception("Call error url : %s" % url)

        return (status_code, response)
