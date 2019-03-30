'''
Created on 11 mrt. 2019

@author: Mohammed el Mochoui
'''

import twitter 
import _pickle as cPickle
from textblob import TextBlob
import re
import csv

CONSUMER_KEY = 'S8ysO5RZ5WRnVw7X9cHnirz9a'
CONSUMER_SECRET = 'u54iVH81OsNrylUEFiS9Kc4DzOjbeYyRBZ5rF5fq1nFQV1SZvd'
OAUTH_TOKEN = '1093508600012652544-3HRLQVyc5nzlFoBs0wqL1ARDEtDW18'
OAUTH_TOKEN_SECRET = 'iWBiRcZwun29ypSiKTfuPXv9ktxj8w5uVho9x6SR6N8Hw'

dictionary = {
                  'Darren Woods': (36665547, "exxon")
                  }

date_dict = {
    "Jan": "01",
    "Feb": "02",
    "Mar": "03",
    "Apr": "04",
    "May": "05",
    "Jun": "06",
    "Jul": "07",
    "Aug": "08",
    "Sep": "09",
    "Oct": "10",
    "Nov": "11",
    "Dec": "12"
}


def read_csv(file_name):
    with open(file_name + ".csv", 'rt') as file:
        reader = csv.reader(file)
        first_list = list(reader)
        return_list = []

        for line in first_list:
            line = line[:2]
            return_list.append(line)

    return return_list


def tweet_cleanup(tweet):
    return ' '.join(re.sub("(@[A-Za-z0-9]+)|([^0-9A-Za-z \t])|(\w+:\/\/\S+)", " ", tweet).split())


def sentiment_analyze(tweet):
    analysis = TextBlob(tweet)

    score = analysis.sentiment.polarity

    if score > 0:
        return "Positive"
    elif score == 0:
        return "Neutral"
    else:
        return "Negative"


def authenticate(oauth_token, oauth_token_secret,consumer_key, consumer_secret):
    auth = twitter.oauth.OAuth(oauth_token, oauth_token_secret,consumer_key, consumer_secret)
    twitter_api = twitter.Twitter(auth=auth)
    return twitter_api


def get_tweets(twitter_api, id, keyword):

    tweets = []
    count = 0

    while count < 6000:
        statuses = twitter_api.statuses.user_timeline(user_id=id, count = 200, include_rts = False)

        for tweet in statuses:
            tweets.append(tweet)
            count += 1

    matching = [str(tweet['id']) + "," + str(tweet["created_at"]) for tweet in tweets if keyword in tweet.get('text')]

    unique_tweets = remove_duplicates(matching)

    tweet_text = [str(tweet['text']) for tweet in tweets if keyword in tweet.get('text')]

    unique_text = remove_duplicates(tweet_text)

    tweets = []

    data_dict = make_dict(keyword)

    for tweet in unique_tweets:
        tweet_id, tweet_date = tweet.split(",")

        tweet_date = tweet_date[26:] + "/" + date_dict[tweet_date[4:7]] + "/" + tweet_date[8:10]

        value = str(data_dict.get(tweet_date))

        tweets.append("https://twitter.com/bramus/status/" + tweet_id + ", " + tweet_date + ", " + value)

    for x in range(len(tweets)):

        sentiment = sentiment_analyze(tweet_cleanup(unique_text[x]))

        tweets[x] = tweets[x] + ", Sentiment: " + sentiment

    return tweets


def make_dict(keyword):
    data = read_csv(keyword)

    for x in range(len(data)):
        if x < len(data) - 1:
            data[x][1] = float(data[x][1]) - float(data[x + 1][1])
            data[x] = (data[x][0], data[x][1])

    del data[-1]

    data_dict = dict(data)

    return data_dict


def save_file(data, file_name):
    f = open(file_name + ".pickle", "wb")
    cPickle.dump(data, f)
    f.close()


def open_file(file_name):
    return cPickle.load(open(file_name + ".pickle"))


def load_tweets_to_file(dict, api):

    total_tweets = 0

    for name, data in dict.items():

        user_id = data[0]
        keyword = data[1]

        tweets = get_tweets(api, user_id, keyword)

        text = ""

        length = len(tweets)

        for tweet in tweets:
            text += tweet + "\n"

        save_file(tweets, name)

        sentiment = []
        change = []

        #print(text)

        for line in re.split('\n', text):
            text = line.split(",")
            if len(text) > 2:

                change.append(text[2])
                sentiment.append(text[3])

        for x in range(len(sentiment)):

            sentiment[x] = sentiment[x][12:]

        hasEffect = 0
        hasNoEffect = 0
        total = 0

        for x in range(len(sentiment)):

            print(f"{sentiment[x]} , {change[x]}")

            if sentiment[x] == "Positive" and change[x] != " None":
                if float(change[x]) > 0:
                    hasEffect += 1
                    total += 1

                else:
                    hasNoEffect += 1
                    total += 1

            if sentiment[x] == "Neutral" and change[x] != " None":
                if float(change[x]) == 0:
                    hasEffect += 1
                    total += 1

                else:
                    hasNoEffect += 1
                    total += 1

            if sentiment[x] == "Negative" and change[x] != " None":
                if float(change[x]) < 0:
                    hasEffect += 1
                    total += 1

                else:
                    hasNoEffect += 1
                    total += 1

        print(name)
        p_effect = round(float(hasEffect) / float(total) * 100, 2)
        p_no_effect = round(float(hasNoEffect) / float(total) * 100, 2)

        print(f"The percentage of tweets that had impact on the stock is {p_effect}% \nThe percentage of tweets that had no impact is {p_no_effect}%")


def remove_duplicates(values):
    output = []
    seen = set()
    for value in values:
        if value not in seen:
            output.append(value)
            seen.add(value)
    return output


def main():
    api = authenticate(OAUTH_TOKEN, OAUTH_TOKEN_SECRET,CONSUMER_KEY, CONSUMER_SECRET)
    load_tweets_to_file(dictionary, api)


if __name__ == '__main__':
    print("The tweets are accessed by: https://twitter.com/bramus/status/{TWEET_ID}")
    main()
