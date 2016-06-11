import os
import praw
import re
import urllib2 as urllib
import requests
import reddit_comment
from prawoauth2 import PrawOAuth2Mini
from time import sleep

#secret variables stored on Heroku
user_agent = os.environ['user_agent']
app_key = os.environ['app_key']
app_secret = os.environ['app_secret']
access_token = os.environ['access_token']
refresh_token = os.environ['refresh_token']
scopes = os.environ['scopes']

reddit_client = praw.Reddit(user_agent=user_agent)
oauth_helper = PrawOAuth2Mini(reddit_client, app_key=app_key, app_secret=app_secret,
			 access_token=access_token, refresh_token=refresh_token, scopes=scopes)

checked_submissions = set()
checked_comments = set()
regex = re.compile(r'(https://(www.)?instagram.com/p/[\w\-]{10,11}/)')
subreddits = ['test', 'MMA', 'bodybuilding', 'SquaredCircle', 'spacex']


def main():
	while True:
		try:
			for subreddit_name in subreddits:
				mirror_submissions(subreddit_name)
				mirror_comments(subreddit_name)

		except praw.errors.OAuthInvalidToken:
			oauth_helper.refresh() #refreshes expired tokens

		except praw.errors.RateLimitExceeded as error:
		           print 'Exceeded commenting limit, have to sleep for %d seconds' % error.sleep_time
		           sleep(error.sleep_time)

		except (requests.exceptions.ReadTimeout, requests.exceptions.ConnectionError, praw.errors.HTTPException):
		 	print "Network problems, will take a short nap"
		 	sleep(30)

		empty_sets_if_big()
		sleep(15)


def mirror_submissions(subreddit_name):
	global checked_submissions
	subreddit = reddit_client.get_subreddit(subreddit_name)

	for submission in subreddit.get_new():
		if submission.id not in checked_submissions:
			insta_links = get_insta_links(submission.url)
			if len(insta_links) > 0:
				if not already_replied(submission.comments):
					bot_comment = reddit_comment.create_comment(insta_links)
					print submission.add_comment(bot_comment)
			checked_submissions.add(submission.id)

			
def get_insta_links(text):
	insta_links = set(regex.findall(text)) #remove duplicate links by using set
	insta_links = filter_dead_links(insta_links)

	#limit links to 5 (5 is an arbitrary number, it could be much higher)
	if len(insta_links) > 5:
		return []
	return insta_links

	
def filter_dead_links(insta_links):
	working_links = []
	for link in insta_links:
		link = link[0] #first regex group, i.e. excluding the 'www.' since its optional
		try :
			urllib.urlopen(link)
			working_links.append(link)
		except:
			pass
			
	return working_links


def already_replied(replies):
	for comment in replies:
		if author_is_bot(comment):
			return True
	return False


def author_is_bot(comment):
	if comment.author != None:
		if comment.author.name == "InstagramMirror":
			return True
	return False


def mirror_comments(subreddit_name):
	global checked_comments

	for comment in reddit_client.get_comments(subreddit_name):
		if comment.id not in checked_comments and not author_is_bot(comment):
			insta_links = get_insta_links(comment.body)
			if len(insta_links) > 0:
				comment.refresh() #redditAPI returns an empty replies list if not refreshed (bug)
				if not already_replied(comment.replies):
					bot_comment = reddit_comment.create_comment(insta_links)
					print comment.reply(bot_comment)
			checked_comments.add(comment.id)


def empty_sets_if_big():
	global checked_comments, checked_submissions

	if len(checked_comments) > 10000:
   		checked_comments = set()
   	if len(checked_submissions)  > 10000:
   		checked_submissions = set()


if __name__ == '__main__':
	main()