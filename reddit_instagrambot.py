import os
import logging
import re as regex
from time import sleep

import praw
from prawoauth2 import PrawOAuth2Mini
from requests.exceptions import ReadTimeout, ConnectionError

import logging.config
from reddit_mirror_handling import MirrorHandler
from reddit_message_handling import MessageHandler
from reddit_comment_handling import CommentHandler

# secret variables stored on Heroku
user_agent = os.environ['user_agent']
app_key = os.environ['app_key']
app_secret = os.environ['app_secret']
access_token = os.environ['access_token']
refresh_token = os.environ['refresh_token']
scopes = os.environ['scopes'].split()

subreddits = ['test', 'MMA', 'bodybuilding', 'SquaredCircle', 'spacex']
logging.config.fileConfig("logging.conf")
logger = logging.getLogger('root')
reddit_client = praw.Reddit(user_agent=user_agent)
bot_account = praw.objects.Redditor(reddit_client, user_name="InstagramMirror")
comment_handler = CommentHandler(logging, bot_account)
message_handler = MessageHandler(reddit_client, comment_handler, regex, logging)
mirror_handler = MirrorHandler(reddit_client, comment_handler, regex, logging)
oauth_helper = PrawOAuth2Mini(
	reddit_client, app_key=app_key, app_secret=app_secret,
	access_token=access_token, refresh_token=refresh_token, scopes=scopes)


def main():
	counter = 0
	while True:
		counter += 1

		try:
			for subreddit_name in subreddits:
				mirror_handler.mirror_submissions(subreddit_name)
				mirror_handler.mirror_comments(subreddit_name)

			if counter % 3 == 0:
				if message_handler.new_messages():
					message_handler.forward_messages(user="bestme")
					message_handler.process_deletion_requests()
					message_handler.mark_messages_as_read()

			if counter % 10 == 0:
				comment_handler.delete_downvoted_comments()

			if counter == 150:
				mirror_handler.empty_checked_comments()
				mirror_handler.empty_checked_submissions()
				counter = 0

		except praw.errors.OAuthInvalidToken:
			logger.warning('Tokens have expired, need to refresh')
			oauth_helper.refresh()

		except praw.errors.RateLimitExceeded as err:
			logger.warning('Exceeded commenting limit, sleeping %ds' % err.sleep_time)
			sleep(err.sleep_time)

		except (ReadTimeout, ConnectionError, praw.errors.HTTPException) as err:
			logger.warning('Network problem: %s, will take a short nap' % err)
			sleep(180)

		sleep(5)


if __name__ == '__main__':
	main()
