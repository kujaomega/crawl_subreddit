
**Assumptions:**

In this project I assume that the reddit endpoint ("/r/Python.json") gives you the latest posts ordered by the recent update.

As there is a throttling time in the api calls, I have not implemented parallellism, the bottleneck is the 600 api calls in 600 seconds.

I have choosen to do use AWS lambdas to make this project as It is a stadistics api and will not have a need to be requested every second. For this reason lambdas will decrease the costs of the api. As AWS have got a free tier of service and Mongodb offer a free database, I have implemented the services in a free way.

To use the service I have created first a Mongodb database and I have stored the dabase information in a mongo_db.json file. To execute the files I assume you are using Ubuntu and you have docker and pyhton3.6 installed. You also need to have AWS credentials stored in your "~/.aws/" folder. First of all, to crawl all the data to the database, execute the reddit_crawler/reddit_crawler.py.
Then you need to execute the reddit_crawler/deploy_lambda.sh to deploy the lambda for constantly update database. You need to execute the api_endpoint/deploy_lambda.sh to create the api endpoints.


**BONUS:**

1.
I choosen the explained architecture for an ease to implement this step.

2.
I have implemented top submitters and top commenters as a personal challenge but I have not implemented the most active users due the lack of time.

3.
I have implemented all posts by user and all posts a user commented as a personal challenge.

4.
I have implemented the average comment karma for a user as a challenge but I have not implemented the top 10 most valued users due the lack of time.

5.
I have implemented a script for deploying the api endpoint buy I have not implemented the tests in the continuous integration due the lack of time.


**ENDPOINTS:**
    The api calls will be available a week or until a response

  GET - https://jg6l4dw34i.execute-api.eu-central-1.amazonaws.com/dev/top10punctuation

    queryparam: rank["all", "discussion" or "external"]
  GET - https://jg6l4dw34i.execute-api.eu-central-1.amazonaws.com/dev/top10comments

    queryparam: rank["all", "discussion" or "external"]
  GET - https://jg6l4dw34i.execute-api.eu-central-1.amazonaws.com/dev/top10submitters

  GET - https://jg6l4dw34i.execute-api.eu-central-1.amazonaws.com/dev/top10commenters

  GET - https://jg6l4dw34i.execute-api.eu-central-1.amazonaws.com/dev/allPostsByUser

    queryparam: author
  GET - https://jg6l4dw34i.execute-api.eu-central-1.amazonaws.com/dev/allPostsByUserComments

    queryparam: author
  GET - https://jg6l4dw34i.execute-api.eu-central-1.amazonaws.com/dev/averageCommentKarma

    queryparam: author
