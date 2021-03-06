class MessageHandler:
	def __init__(self, reddit_client, comment_handler, regex, logging):
		self._reddit_client = reddit_client
		self._comment_handler = comment_handler
		self._regex = regex
		self._logger = logging.getLogger('messaging')
		self._unread = []
		self._accepted_deletions = []
		self._denied_deletions = []

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
		else:
			body_split = msg.body.split()
			if self._regex.search(r't1_', body_split[1]):
				comment = self._reddit_client.get_info(thing_id=body_split[1])
				context = comment.permalink + "?context=10000"
				msg.context = "[context](%s)" % context

		body = "%s\n\n%s\n\nby /u/%s" % (msg.context, msg.body, msg.author.name)
		return body

	def process_deletion_requests(self):
		self._filter_requests()

		for (comment, user) in self._accepted_deletions:
			self._comment_handler.delete_comment(comment)
			self._reply_with_delete_confirmation(user)

		for user in self._denied_deletions:
			self._reply_with_delete_denial(user)

	def _filter_requests(self):
		self._accepted_deletions = []
		self._denied_deletions = []

		for msg in self._unread:
			body = msg.body.split()
			if self._message_is_removal_request(body):
				valid, comment = self._validate_request(body, msg)
				if valid:
					self._logger.info("valid delete request")
					self._accepted_deletions.append((comment, msg.author.name))
				else:
					self._logger.info("not valid delete request")
					self._denied_deletions.append(msg.author.name)

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
		# If the parent author is None then the comment was deleted, and it is now
		# impossible to check if it was the user of the parent comment who made the
		# request. So if the comment was deleted the choices are then to either deny
		# all request, allow all requests, or manually making judgement calls on all
		# request. This bot allows all requests on deleted comments.
		if parent.author is None or parent.author.name == msg.author.name:
			return True
		return False

	def _reply_with_delete_confirmation(self, user):
		subject = "Mirror deleted"
		body = "The instagram mirror has been deleted"
		self._reddit_client.send_message(user, subject, body)
		self._logger.info("replied with delete confirmation")

	def _reply_with_delete_denial(self, user):
		subject = "Deletion request denied"
		body = "Only the user of the original post can request mirror deletion."
		self._reddit_client.send_message(user, subject, body)
		self._logger.info("replied with delete denial")

	def mark_messages_as_read(self):
		for msg in self._unread:
			msg.mark_as_read()
		self._unread = []
		self._logger.info("messages marked as read")
