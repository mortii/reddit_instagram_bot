import os
import praw
from prawoauth2 import PrawOAuth2Mini
from instagramScraper import Instagram
import re
from time import sleep
import urllib2 as urllib
import requests


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
footer = ("^I'm ^a ^bot. [^[Report ^Bug]]"
	"(https://np.reddit.com/message/compose/?to=bestme&amp;subject=InstagramMirror%20bug)"
	"[^[Give ^Feedback ^or ^Suggestions]]"
	"(https://np.reddit.com/message/compose/?to=bestme&amp;subject=InstagramMirror%20feedback/suggestion)"
	"[^[Source ^Code]](https://github.com/mortii/reddit_instagram_bot)")
comment_length_error = ("Sorry, caption(s) too long for a reddit comment."
			"(If you think this is a bug let me know)\n\n***\n\n")


def main():
	while True:
		try:
			for subreddit_name in subreddits:
				mirror_submissions(subreddit_name)
				mirror_comments(subreddit_name)

		except praw.errors.OAuthInvalidToken:
			oauth_helper.refresh() 

		except praw.errors.RateLimitExceeded as error:
		           print 'Exceeded commenting limit, have to sleep for %d seconds' % error.sleep_time
		           sleep(error.sleep_time)

		except requests.exceptions.ReadTimeout:
		 	print "Read timeout"
		 	sleep(15)

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
					bot_comment = create_comment(insta_links)
					print submission.add_comment(bot_comment)
			checked_submissions.add(submission.id)

			
def get_insta_links(text):
	insta_links = set(regex.findall(text)) 
	insta_links = filter_dead_links(insta_links)

	#limit links to 5 (5 is an arbitrary number, it could be much higher)
	if len(insta_links) > 5:
		return []
	return insta_links

	
def filter_dead_links(insta_links):
	working_links = []
	for link in insta_links:
		link = link[0] #first regex group
		try :
			url_reader = urllib.urlopen(link)
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


def create_comment(insta_links):
	total_comment = "" 
	for link in insta_links:
		insta = Instagram(link)
		header = '[**%s(%s):**](%s)' % (insta.title, insta.user, insta.url)
		time = '\n\n>^(%s)' % insta.time
		media_mirror = "\n\n>[[%s Mirror]](%s)" % (insta.media, insta.mirror_url)
		caption = '\n\n>%s\n\n***\n\n' % insta.caption
		total_comment += header + time + media_mirror + caption
	total_comment += footer

	if len(total_comment) >= 10000:
		total_comment = comment_length_error + footer
	return total_comment


def mirror_comments(subreddit_name):
	global checked_comments

	for comment in reddit_client.get_comments(subreddit_name):
		if comment.id not in checked_comments and not author_is_bot(comment):
			insta_links = get_insta_links(comment.body)
			if len(insta_links) > 0:
				comment.refresh() #have to refresh due to redditAPI bug causing empty replies list
				if not already_replied(comment.replies):
					bot_comment = create_comment(insta_links)
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