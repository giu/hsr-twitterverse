from flask import Flask, render_template
from time import strftime
from werkzeug.contrib.cache import SimpleCache
import feedparser
import re

app = Flask(__name__)
cache = SimpleCache()

CACHEKEY_TWEETS = "tweets"
CACHEKEY_PARTICIPANTS = "participants"
CACHETIMEOUT_TWEETS = 30
CACHETIMEOUT_PARTICIPANTS = 180

def __get_from_cache(cachekey, cachetimeout, getter):
    item = cache.get(cachekey)

    if item is None:
        item = getter()
        cache.set(cachekey,item,cachetimeout)
    
    return item

def __get_tweets_from_feed():
    hsrFeed = feedparser.parse("http://pipes.yahoo.com/pipes/pipe.run?_id=zCBrTxw03hG8mv1uPm7D0g&_render=rss")

    tweets = []

    for item in hsrFeed["items"]:
        user,delim,tweet = item.title.partition(":")

        date = strftime("%d.%m.%Y @ %H:%M", item.updated_parsed)

        #Replace URLs with a link
        tweet = re.sub("http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+~]|[!*\(\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+", lambda m: "<a href='%s'>%s</a>" % (m.group(0), m.group(0)), tweet)
        #Replace hashtags with a link to Twitter's search
        tweet = re.sub("(#[a-zA-Z0-9_]+)", lambda m: "<a href='https://search.twitter.com/search?q=%s'>%s</a>" % (m.group(0), m.group(0)), tweet)
        #Replace usernames with a link to the user's Twitter page
        tweet = re.sub("@([a-zA-Z0-9_]+)", lambda m: "<a href='https://twitter.com/%s'>%s</a>" % (m.group(1), m.group(0)), tweet)

        tweets.append((user,tweet,item.link,date))
    
    return tweets

#Implementation of the lucky sort algorithm (http://xlinux.nist.gov/dads/HTML/luckySort.html)
def __get_participants_list():
    return ["_giu", "cmenzi", "cocaman", "domueni", "erelguitars", "floel", "FlohEinstein", "kung_foo", "m_st", "mavonair", "merze", "miguelgalaxy", "modsteve", "odi86", "pboos", "qinobi", "ret0", "sfkeller", "shdhsr", "suls", "Supertext", "tremendez"]

def get_tweets():
    return __get_from_cache(CACHEKEY_TWEETS, CACHETIMEOUT_TWEETS, __get_tweets_from_feed)

def get_participants():
    return __get_from_cache(CACHEKEY_PARTICIPANTS, CACHETIMEOUT_PARTICIPANTS, __get_participants_list)

@app.route("/")
def show_tweets():
    return render_template("show_tweets.html", tweets = get_tweets(), participants = get_participants())

if __name__ == "__main__":
    app.run()