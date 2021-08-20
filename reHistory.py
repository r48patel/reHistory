#!/usr/bin/env python3.7
import requests
from dotenv import load_dotenv
from os import environ
import praw

load_dotenv()

reddit = praw.Reddit(
    client_id=environ.get("CLIENT_ID"),
    client_secret=environ.get("CLIENT_SECRET"),
    user_agent="reHistory:v0.0 (by /u/r48patel)",
)

# https://praw.readthedocs.io/en/latest/code_overview/models/redditor.html?highlight=get_comments#praw.models.Redditor.comments
# https://praw.readthedocs.io/en/latest/code_overview/other/sublisting.html#praw.models.listing.mixins.redditor.SubListing
# https://www.reddit.com/r/botwatch/comments/2v13eb/how_to_get_all_comments_of_a_reddit_user_by_using/


def user_comments(user, debug=False):
    user = reddit.redditor('r48patel')
    comments = list(user.comments.new(limit=None))
    subreddit_comments_dict = {}
    for comment in comments:
        subreddit_comments_dict.setdefault(comment.subreddit.display_name, [])
        subreddit_comments_dict[comment.subreddit.display_name].append(comment.body)

    if debug:
        for subreddit in subreddit_comments_dict.keys():
            print(subreddit)
            print(subreddit_comments_dict[subreddit])
            print()

    return subreddit_comments_dict

if __name__ == '__main__':
    user_comments('r48patel', debug=True)
