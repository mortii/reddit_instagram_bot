import urllib2 as urllib


class MirrorHandler:
	def __init__(self, reddit_client, comment_handler, regex, logging):
		self._reddit_client = reddit_client
		self._comment_handler = comment_handler
		self._regex = regex
		_INSTAGRAM_PATTERN = r'(https://(www.)?instagram.com/p/[\w\-]{10,11}/)'
		self._regex_instagram = regex.compile(_INSTAGRAM_PATTERN)
		self._logger = logging.getLogger('mirroring')
		self._checked_comments = set()
		self._checked_submissions = set()

	def mirror_submissions(self, subreddit_name):
		subreddit = self._reddit_client.get_subreddit(subreddit_name)
		for submission in subreddit.get_new():
			if submission.id in self._checked_submissions:
				break

			self._checked_submissions.add(submission.id)
			has_links, insta_links = self._get_insta_links(submission.url)

			if has_links and not self._already_replied(submission.comments):
				self._comment_handler.add_comment(insta_links, submission=submission)

	def _get_insta_links(self, text):
		all_insta_links = self._regex_instagram.findall(text)
		unique_insta_links = set(all_insta_links)
		working_insta_links = self._filter_dead_links(unique_insta_links)

		# limit links to 5 to avoid huge comments
		if len(working_insta_links) > 5 or len(working_insta_links) == 0:
			return False, []
		return True, working_insta_links

	def _filter_dead_links(self, insta_links):
		working_links = []
		for link in insta_links:
			link = link[0]   # excluding 'www.' since it's optional
			try:
				urllib.urlopen(link)
				working_links.append(link)
			except urllib.HTTPError:
				pass
		return working_links

	def _already_replied(self, replies):
		for comment in replies:
			if self._made_by_bot(comment):
				return True
		return False

	def _made_by_bot(self, comment):
		if comment.author is not None:
			if comment.author.name == "InstagramMirror":
				return True
		return False

	def mirror_comments(self, subreddit_name):
		for comment in self._reddit_client.get_comments(subreddit_name, sort=u'new'):
			if comment.id in self._checked_comments:
				break

			self._checked_comments.add(comment.id)
			if self._made_by_bot(comment):
				break

			has_links, insta_links = self._get_insta_links(comment.body)

			try:
				comment.refresh()  # redditAPI returns no replies unless refreshed (bug)
			except IndexError:
				pass

			if has_links and not self._already_replied(comment.replies):
				self._comment_handler.add_comment(insta_links, comment=comment)

	def empty_checked_comments(self):
		self._checked_comments = set()
		self._logger.info('emptied checked_comments')

	def empty_checked_submissions(self):
		self._checked_submissions = set()
		self._logger.info('emptied checked_submissions')
