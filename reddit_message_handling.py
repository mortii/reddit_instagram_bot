class Message_handler:
	def __init__(self, reddit_client, regex, logging):
		self.reddit_client = reddit_client
		self.regex = regex
		self.logger = logging.getLogger('messaging')
		self.unread = []
		self.accepted_deletions = []
		self.denied_deletions = []


	def new_messages(self):
		unread_generator = self.reddit_client.get_unread()
		unread = [message for message in unread_generator]

		if len(unread) > 0:
			self.logger.info("new messages")
			self.unread = unread
			return True
		else:
			self.unread = []
			return False

			
	def forward_messages(self, user):	
		for msg in self.unread:
			body = self.create_message_body(msg)
			self.reddit_client.send_message(user, msg.subject, body)
		self.logger.info("forwarded messages")


	def create_message_body(self, msg):
		if msg.context != "":
			msg.context = "[context](%s)" % msg.context
		body = "%s\n\n%s\n\nby /u/%s" % (msg.context, msg.body, msg.author.name)
		return body


	def process_delete_requests(self):
		self.accepted_deletions = []
		self.denied_deletions = []

		for msg in self.unread:
			body = msg.body.split()
			if self.message_is_removal_request(body):
				valid, comment = self.validate_request(body, msg)
				if valid:
					self.logger.info("valid delete request")
					self.accepted_deletions.append((comment, msg.author.name))
				else:
					self.logger.info("not valid delete request")
					self.denied_deletions.append(msg.author.name)	


	def message_is_removal_request(self, body):
		if body[0] == 'delete' and self.regex.search(r't1_', body[1]):
			self.logger.info("message is delete request")
			return True
		self.logger.info("message is not delete request")
		return False


	def validate_request(self, body, msg):
		comment, parent = self.try_to_get_comment_and_parent(body, msg)
		if comment != None and parent != None:
			if self.valid_request_author(parent, msg):
				return True, comment
		return False, None


	def try_to_get_comment_and_parent(self, body, msg):
		try:
			comment = self.reddit_client.get_info(thing_id=body[1])
			if comment.author.name == "InstagramMirror":
				parent = self.reddit_client.get_info(thing_id=comment.parent_id) 
				return comment, parent
			else:
				return None, None
		except:
			return None, None


	def valid_request_author(self, parent, msg):
		if parent.author.name != None:
			if parent.author.name == msg.author.name:
				return True
		return False


	def reply_with_delete_confirmation(self, user):
		subject = "deleted"
		body = "the mirror has been deleted"
		self.reddit_client.send_message(user, subject, body)
		self.logger.info("replied with delete confirmation")


	def reply_with_delete_denial(self, user):
		subject = "denied"
		body = "only the user of the original post can request mirror deletion"
		self.reddit_client.send_message(user, subject, body)
		self.logger.info("replied with delete denial")


	def mark_messages_as_read(self):
		for msg in self.unread:
			msg.mark_as_read()
		self.unread = []
		self.logger.info("messages marked as read")