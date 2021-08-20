#!/usr/bin/env python3.7
import requests
from dotenv import load_dotenv
from os import environ
import datetime
import praw
import logging

LOGGING_LEVEL = logging.INFO

handler = logging.StreamHandler()
handler.setLevel(LOGGING_LEVEL)
for logger_name in ("praw", "prawcore", "urllib3.connectionpool"):
    logger = logging.getLogger(logger_name)
    logger.setLevel(LOGGING_LEVEL)
    logger.addHandler(handler)

load_dotenv()

reddit = praw.Reddit(
    check_for_async=True,
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
    def __init__(self, created, thread_title, body, body_html, link, is_top_comment, parent_comment):
        self.created = created
        self.thread_title = thread_title
        self.body = body
        self.body_html = \
            body_html.replace('<p>', '').replace('</p>', '').replace('<div class="md">', '').replace('</div>', '')
        self.link = "https://www.reddit.com{}".format(link)
        self.is_top_comment = is_top_comment
        self.parent_comment = parent_comment

    def __str__(self):
        return "created: {}\n" \
               "thread_title: {}\n" \
               "body: {}\n" \
               "body_html: {}" \
               "".format(self.created, self.thread_title, self.body, self.body_html)

    def __repr__(self):
        return "created: {}\n" \
               "thread_title: {}\n" \
               "body: {}\n" \
               "body_html: {}" \
               "".format(self.created, self.thread_title, self.body, self.body_html)

# https://praw.readthedocs.io/en/latest/code_overview/models/redditor.html?highlight=get_comments#praw.models.Redditor.comments
# https://praw.readthedocs.io/en/latest/code_overview/other/sublisting.html#praw.models.listing.mixins.redditor.SubListing
# https://www.reddit.com/r/botwatch/comments/2v13eb/how_to_get_all_comments_of_a_reddit_user_by_using/


def user_comments(user, debug=logging.INFO):
    user = reddit.redditor(user)
    comments = user.comments.new(limit=None)
    subreddit_comments_dict = {}
    for comment in comments:
        # print("Start:", datetime.datetime.now())
        # subreddit = Subreddit(comment.subreddit.display_name, comment.subreddit.public_description)
        subreddit = comment.subreddit.display_name
        # print("Created subreddit:", datetime.datetime.now())
        # print("is {} in subreddit_comments_dict?: {}".format(subreddit, subreddit in subreddit_comments_dict.keys()))
        subreddit_comments_dict.setdefault(subreddit, [])
        # print("Set Default:", datetime.datetime.now())
        submission_title = comment.submission.title
        comment_parent_id = comment.parent_id
        comment_parent_comment = None
        comment_is_top = True
        if comment.parent_id.startswith('t1'):
            parent_comment = reddit.comment(comment_parent_id)
            comment_parent_comment = Comment(
                parent_comment.created_utc,
                submission_title,
                parent_comment.body,
                parent_comment.body_html,
                parent_comment.permalink,
                True,
                None
            )
            comment_is_top = False

        subreddit_comments_dict[subreddit].append(
            Comment(
                comment.created_utc,
                submission_title,
                comment.body,
                comment.body_html,
                comment.permalink,
                comment_is_top,
                comment_parent_comment
            )
        )
        # print("Finish:", datetime.datetime.now())

    if debug == logging.DEBUG:
        for subreddit in subreddit_comments_dict.keys():
            print(subreddit)
            print(subreddit_comments_dict[subreddit])
            print()

    return subreddit_comments_dict


if __name__ == '__main__':
    user_comments('r48patel', debug=True)
