class MessageHandler:
	def __init__(self, reddit_client, regex, logging):
		self._reddit_client = reddit_client
		self._regex = regex
		self._logger = logging.getLogger('messaging')
		self._unread = []
		self.accepted_deletions = []
		self.denied_deletions = []

	def new_messages(self):
		unread_generator = self._reddit_client.get_unread()
		unread = [message for message in unread_generator]

		if len(unread) > 0:
			self._logger.info("new messages")
			self._unread = unread
			return True
		else:
			self._unread = []
			return False

	def forward_messages(self, user):
		for msg in self._unread:
			body = self._create_message_body(msg)
			self._reddit_client.send_message(user, msg.subject, body)
		self._logger.info("forwarded messages")

	def _create_message_body(self, msg):
		if msg.context != "":
			msg.context = "[context](%s)" % msg.context
		body = "%s\n\n%s\n\nby /u/%s" % (msg.context, msg.body, msg.author.name)
		return body

	def process_delete_requests(self):
		self.accepted_deletions = []
		self.denied_deletions = []

		for msg in self._unread:
			body = msg.body.split()
			if self._message_is_removal_request(body):
				valid, comment = self._validate_request(body, msg)
				if valid:
					self._logger.info("valid delete request")
					self.accepted_deletions.append((comment, msg.author.name))
				else:
					self._logger.info("not valid delete request")
					self.denied_deletions.append(msg.author.name)

	def _message_is_removal_request(self, body):
		if body[0] == 'delete' and self._regex.search(r't1_', body[1]):
			self._logger.info("message is delete request")
			return True
		self._logger.info("message is not delete request")
		return False

	def _validate_request(self, body, msg):
		comment, parent = self._try_to_get_comment_and_parent(body, msg)
		if comment is not None and parent is not None:
			if self._valid_request_author(parent, msg):
				return True, comment
		return False, None

	def _try_to_get_comment_and_parent(self, body, msg):
		try:
			comment = self._reddit_client.get_info(thing_id=body[1])
			if comment.author.name == "InstagramMirror":
				parent = self._reddit_client.get_info(thing_id=comment.parent_id)
				return comment, parent
			else:
				return None, None
		except AttributeError:
			return None, None

	def _valid_request_author(self, parent, msg):
		if parent.author is not None:
			if parent.author.name == msg.author.name:
				return True
		return False

	def reply_with_delete_confirmation(self, user):
		subject = "deleted"
		body = "the mirror has been deleted"
		self._reddit_client.send_message(user, subject, body)
		self._logger.info("replied with delete confirmation")

	def reply_with_delete_denial(self, user):
		subject = "denied"
		body = "only the user of the original post can request mirror deletion"
		self._reddit_client.send_message(user, subject, body)
		self._logger.info("replied with delete denial")

	def mark_messages_as_read(self):
		for msg in self._unread:
			msg.mark_as_read()
		self._unread = []
		self._logger.info("messages marked as read")
