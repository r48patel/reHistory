#!/usr/bin/env python3.7
import requests
from dotenv import load_dotenv
from os import environ
import datetime
import praw
import re

load_dotenv()

reddit = praw.Reddit(
    client_id=environ.get("CLIENT_ID"),
    client_secret=environ.get("CLIENT_SECRET"),
    user_agent="reHistory:v0.0 (by /u/r48patel at {})".format(datetime.datetime.now()),
)


class Subreddit:
    def __init__(self, display_name, public_description):
        self.display_name = display_name
        self.public_description = public_description

    def __hash__(self):
        return hash((self.display_name, self.public_description))

    def __eq__(self, other):
        return (self.display_name, self.public_description) == (other.display_name, other.public_description)

    def __str__(self):
        return self.display_name

    def __repr__(self):
        return self.display_name


class Comment:
    def __init__(self, body, body_html):
        self.body = body
        self.body_html = \
            body_html.replace('<p>', '').replace('</p>', '').replace('<div class="md">', '').replace('</div>', '')

    def __str__(self):
        return "body: {}\nbody_html: {}".format(self.body, self.body_html)

    def __repr__(self):
        return "body: {}\nbody_html: {}".format(self.body, self.body_html)

# https://praw.readthedocs.io/en/latest/code_overview/models/redditor.html?highlight=get_comments#praw.models.Redditor.comments
# https://praw.readthedocs.io/en/latest/code_overview/other/sublisting.html#praw.models.listing.mixins.redditor.SubListing
# https://www.reddit.com/r/botwatch/comments/2v13eb/how_to_get_all_comments_of_a_reddit_user_by_using/


def user_comments(user, debug=False):
    user = reddit.redditor(user)
    comments = list(user.comments.new(limit=None))
    subreddit_comments_dict = {}
    for comment in comments:
        subreddit = Subreddit(comment.subreddit.display_name, comment.subreddit.public_description)
        # print("is {} in subreddit_comments_dict?: {}".format(subreddit, subreddit in subreddit_comments_dict.keys()))
        subreddit_comments_dict.setdefault(subreddit, [])
        subreddit_comments_dict[subreddit].append(Comment(comment.body, comment.body_html))

    if debug:
        for subreddit in subreddit_comments_dict.keys():
            print(subreddit)
            print(subreddit_comments_dict[subreddit])
            print()

    return subreddit_comments_dict

if __name__ == '__main__':
    user_comments('r48patel', debug=True)
