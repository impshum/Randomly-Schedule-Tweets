import tweepy
from requests import get
from requests.exceptions import ConnectionError
from tinydb import TinyDB, Query
from time import sleep
import schedule
import re
import sys
import configparser
from argparse import ArgumentParser

p = ArgumentParser(description="Randomly Schedule Tweets")

p.add_argument('-t', '--tweet', action='store_true', help='read from the database and tweet')
p.add_argument('-w', '--write', action='store_true', help='write to the database from input.txt')
p.add_argument('-c', '--clear', action='store_true', help='delete all in the database')
args = p.parse_args()

config = configparser.ConfigParser()
config.read('conf.ini')
consumer_key = config['TWITTER']['consumer_key']
consumer_secret = config['TWITTER']['consumer_secret']
access_key = config['TWITTER']['access_key']
access_secret = config['TWITTER']['access_secret']
input_file = config['SETTINGS']['input_file']
database_file = config['SETTINGS']['database_file']
image_directory = config['SETTINGS']['image_directory']
min_sleep = int(config['SETTINGS']['min_sleep'])
max_sleep = int(config['SETTINGS']['max_sleep'])
test_mode = int(config['TEST-MODE']['test_mode'])

db = TinyDB(database_file)
db_query = Query()


def wait_until_online(timeout, slumber):
    offline = 1
    while offline:
        try:
            r = get("https://google.com", timeout=timeout).status_code
        except ConnectionError:
            r = None
        if r == 200:
            offline = 0
        else:
            print('OFFLINE - Sleeping for 15 minutes')
            sleep(slumber)


def read_input():
    with open(input_file) as f:
        lines = f.readlines()

    for line in lines:
        parts = line.strip().split('|')
        title = parts[0]
        image = parts[1]
        print(f'{title} - {image}')
        add_to_db(title, image, 0)


def read_db(api):
    db_count = len(db.all())
    c = 0

    for item in db:
        title = item['title']
        image = item['image']
        tweeted = item['tweeted']
        if not tweeted:
            wait_until_online(10, 900)
            post_tweet(api, title, image)
            print(f'Tweeting {title}')
        else:
            print(f'Already tweeted {title}')
            c += 1

    if db_count - c == 0:
        print('No more tweets to post - Exiting')
        sys.exit()


def add_to_db(title, image, tweeted):
    if not db.search(db_query.title == title):
        db.insert({'title': title, 'image': image, 'tweeted': tweeted})
        print('Added to db')
    else:
        print('Already exists in db')


def post_tweet(api, title, image):
    image = f'{image_directory}{image}'
    if not test_mode:
        api.update_with_media(image, title)
        db.update({'tweeted': 1}, db_query.title == title)


def main():
    if args.clear:
        db.purge()
        print('Deleted all in db')
    elif not args.tweet and not args.write:
        print('Use -t to read from the database and tweet\nUse -w to write to the database from input.txt\nUse -c to delete all in the database')
    elif args.tweet:
        wait_until_online(10, 900)
        auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
        auth.set_access_token(access_key, access_secret)
        api = tweepy.API(auth)
        read_db(api)
        schedule.every(min_sleep).to(max_sleep).minutes.do(read_db)
        while True:
            schedule.run_pending()
            sleep(1)
    elif args.write:
        read_input()


if __name__ == '__main__':
    main()
