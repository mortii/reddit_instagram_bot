import urllib2 as urllib


class Mirror_handler:
	def __init__(self, reddit_client, comment_handler, regex, logging):
		self.reddit_client = reddit_client
		self.comment_handler = comment_handler
		self.regex = regex
		self.regex_instagram = regex.compile(r'(https://(www.)?instagram.com/p/[\w\-]{10,11}/)')
		self.logger = logging.getLogger('mirroring')
		self.checked_comments = set()
		self.checked_submissions = set()


	def mirror_submissions(self, subreddit_name):
		subreddit = self.reddit_client.get_subreddit(subreddit_name)

		for submission in subreddit.get_new():
			if submission.id not in self.checked_submissions:
				insta_links = self.get_insta_links(submission.url)
				if len(insta_links) > 0:
					if not self.already_replied(submission.comments):
						self.comment_handler.add_comment(insta_links, submission=submission)
				self.checked_submissions.add(submission.id)

				
	def get_insta_links(self, text):
		insta_links = set(self.regex_instagram.findall(text)) #remove duplicate links by using set
		insta_links = self.filter_dead_links(insta_links)

		#limit links to 5 in order to avoid huge comments
		if len(insta_links) > 5:
			return []
		return insta_links

		
	def filter_dead_links(self, insta_links):
		working_links = []
		for link in insta_links:
			link = link[0] #first regex group, i.e. excluding the 'www.' since its optional
			try :
				urllib.urlopen(link)
				working_links.append(link)
			except:
				pass
				
		return working_links


	def already_replied(self, replies):
		for comment in replies:
			if self.author_is_bot(comment):
				return True
		return False


	def author_is_bot(self, comment):
		if comment.author != None:
			if comment.author.name == "InstagramMirror":
				return True
		return False


	def mirror_comments(self, subreddit_name):
		for comment in self.reddit_client.get_comments(subreddit_name):
			if comment.id not in self.checked_comments and not self.author_is_bot(comment):
				insta_links = self.get_insta_links(comment.body)
				if len(insta_links) > 0:
					comment.refresh() #redditAPI returns an empty replies list if not refreshed (bug)
					if not self.already_replied(comment.replies):
						self.comment_handler.add_comment(insta_links, comment=comment)
				self.checked_comments.add(comment.id)


	def empty_checked_comments(self):
		self.checked_comments = set()
		self.logger.info('emptied checked_comments')	


	def empty_checked_submissions(self):
		self.checked_submissions = set()
		self.logger.info('emptied checked_submissions')