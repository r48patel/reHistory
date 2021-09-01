#!/usr/bin/env python3.7
import requests
from requests_futures.sessions import FuturesSession
from dotenv import load_dotenv
from os import environ
import datetime
import praw
import html
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


class ParentComment:
    def __init__(self, url, comment_title):
        self.url = url
        self.comment_title = comment_title
        self.comment = None

    def populate_comment(self):
        # print(self.url.result().json())
        for result in self.url.result().json():
            if result['data']['children'][0]['kind'] == 't1':
                parent_comment_data = result['data']['children'][0]['data']
                self.comment = Comment(
                    parent_comment_data['name'],
                    parent_comment_data['created_utc'],
                    self.comment_title,
                    None,
                    parent_comment_data['body'],
                    parent_comment_data['body_html'],
                    parent_comment_data['permalink'],
                    False,
                    None
                )

    def get_comment(self):
        if not self.comment:
            self.populate_comment()

        return self.comment


class Comment:
    def __init__(self, name, created, thread_title, thread_link, body, body_html, body_link, is_reply, parent_comment):
        self.name = name
        self.created = created
        self.thread_title = thread_title
        self.thread_link = thread_link
        self.body = body
        self.body_html = html.unescape(body_html)\
            .replace('<p>', '')\
            .replace('</p>', '')\
            .replace('<div class="md">', '')\
            .replace('</div>', '')
        self.body_link = "https://www.reddit.com{}".format(body_link)
        self.is_reply = is_reply
        self.parent_comment = parent_comment

    def __str__(self):
        return "created: {}\n" \
               "thread_title: {}\n" \
               "body: {}\n" \
               "body_html: {}" \
               "".format(self.created, self.thread_title, self.body, self.body_html)

    def __repr__(self):
        return "created: {} ... " \
               "thread_title: {} ... " \
               "body: {} ... " \
               "body_html: {}" \
               "".format(self.created, self.thread_title, self.body, self.body_html)


def get_comments(user, after=''):
    start_time = datetime.datetime.now()
    session = FuturesSession(max_workers=10)
    comments_list = []
    r = requests.get("https://www.reddit.com/user/{}/comments.json".format(user),
                     headers={'User-agent': "reHistory:v0.0 (by /u/r48patel at {})".format(datetime.datetime.now())},
                     params={'after': after, 'limit': 100, 'sort': 'new'})
    value = r.json()
    subreddit_comments_dict = {}

    for child in value['data']['children']:
        comment_data = child['data']
        comment_link = comment_data['link_permalink']
        comment_title = comment_data['link_title']
        comment_is_reply = False
        comment_parent_comment = None
        comment_parent_id = comment_data['parent_id']
        subreddit = comment_data['subreddit']
        subreddit_comments_dict.setdefault(subreddit, [])

        if comment_parent_id.startswith('t1'):
            comment_is_reply = True
            url = f"{comment_link}{comment_parent_id.replace('t1_', '')}.json"
            comment_parent_comment = ParentComment(
                session.get(url, headers={'User-agent': "reHistory:v0.0 (by /u/r48patel)"}),
                comment_title
            )

        comment = Comment(
            comment_data['name'],
            comment_data['created_utc'],
            comment_title,
            comment_data['link_permalink'],
            comment_data['body'],
            comment_data['body_html'],
            comment_data['permalink'],
            comment_is_reply,
            comment_parent_comment
        )

        subreddit_comments_dict[subreddit].append(comment)

    comments_list.append(subreddit_comments_dict)

    if value['data']['after']:
        after_dict = get_comments(user, value['data']['after'])
        for subreddit in after_dict.keys():
            if subreddit in subreddit_comments_dict.keys():
                subreddit_comments_dict[subreddit].append(after_dict[subreddit])
            else:
                subreddit_comments_dict[subreddit] = after_dict[subreddit]

    finish_time = datetime.datetime.now()
    print(f"Total Time: {finish_time - start_time}")
    return subreddit_comments_dict


def get_comments_praw(user, debug=logging.INFO):
    user = reddit.redditor(user)
    comments = user.comments.new(limit=None)
    subreddit_comments_dict = {}
    for comment in comments:
        # subreddit = Subreddit(comment.subreddit.display_name, comment.subreddit.public_description)
        subreddit = comment.subreddit.display_name
        subreddit_comments_dict.setdefault(subreddit, [])
        submission_title = comment.submission.title
        comment_parent_id = comment.parent_id
        comment_parent_comment = None
        comment_is_reply = False
        if comment_parent_id.startswith('t1'):
            parent_comment = reddit.comment(comment_parent_id)
            comment_parent_comment = Comment(
                parent_comment.name,
                parent_comment.created_utc,
                submission_title,
                parent_comment.body,
                parent_comment.body_html,
                parent_comment.permalink,
                False,
                None
            )
            comment_is_reply = True

        comment = Comment(
            comment.name,
            comment.created_utc,
            submission_title,
            comment.body,
            comment.body_html,
            comment.permalink,
            comment_is_reply,
            comment_parent_comment
        )
        print("get_comments_praw.body_html: " + comment.body_html)
        subreddit_comments_dict[subreddit].append(comment)

    if debug == logging.DEBUG:
        for subreddit in subreddit_comments_dict.keys():
            print(subreddit)
            print(subreddit_comments_dict[subreddit])
            print()

    return subreddit_comments_dict


if __name__ == '__main__':
    comment_list = get_comments('r48patel')
    # for comment in comment_list['formula1']:
    #     print(comment, comment.body_html)
    # for subreddit in comment_list.keys():
    #     print("{} - {}".format(subreddit, len(comment_list[subreddit])))
