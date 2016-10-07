# -*- coding: utf-8 -*-
from time import sleep
from instagram_scraper import Instagram


_report_bug = (
	u"^[Report Bug](https://reddit.com/message/compose/?to=bestme"
	u"&amp;subject=InstagramMirror%20bug&message={permalink}%20has%20a%20bug)")

_FEEDBACK = (
	u" ^| ^[Feedback/Suggestions?](https://reddit.com/message/compose/?to=bestme"
	u"&amp;subject=InstagramMirror%20feedback/suggestion)")

_delete = (
	u" ^| ^[Delete](https://reddit.com/message/compose/?to=InstagramMirror"
	u"&amp;subject=InstagramMirror%20delete&message="
	u"delete%20{thing_id}%20\(only%20the%20user%20of%20the%20original"
	u"%20post%20can%20do%20this\))")

_SOURCE_CODE = (
	u" ^| ^[Source Code](https://github.com/mortii/"
	u"reddit_instagram_bot)")


class CommentHandler:
	def __init__(self, logging):
		self._logger = logging.getLogger('commenting')

	def add_comment(self, insta_links, submission=None, comment=None):
		body = self._create_body(insta_links)
		footer = _report_bug + _FEEDBACK + _delete + _SOURCE_CODE
		bot_comment = body + footer

		if submission is not None:
			praw_comment = submission.add_comment(bot_comment)
		else:
			praw_comment = comment.reply(bot_comment)

		self._logger.info(praw_comment)
		sleep(5)
		self._update_footer(praw_comment, body, footer)

	def _create_body(self, insta_links):
		comment_body = ""
		for link in insta_links:
			insta = Instagram(link)
			header = '[**%s(%s):**](%s)' % (insta.title, insta.user, insta.url)
			time = '\n\n>^(%s)' % insta.time
			media_mirror = "\n\n>[[%s Mirror]](%s)" % (insta.media, insta.mirror_url)
			caption = '\n\n>%s\n\n***\n\n' % insta.caption
			comment_body += header + time + media_mirror + caption

		if len(comment_body) > 5000:
			comment_body = "Sorry, caption(s) too long for reddit.\n\n***\n\n'"
		return comment_body

	def _update_footer(self, praw_comment, body, footer):
		# The comment permalink and id is added to the footer to allow for an
		# automated comment deletion process and to make debugging easier.
		# This can only be done by editing the comment after it is posted.
		permalink = praw_comment.permalink
		thing_id = praw_comment.name
		comment = body + footer.format(permalink=permalink, thing_id=thing_id)
		praw_comment.edit(comment)
		self._logger.debug("updated footer links")

	def delete_comment(self, praw_comment):
		# Once a valid deletion request has been received the content of the comment
		# will be edited out and the 'delete' link will be removed from the footer.
		# Edit is used in place of delete because the bot might create a new mirror
		# in place of the deleted one after a failure because the bot it only uses
		# volatile memory, but also checks if it's already replied. Another advantage
		# editing has over deleting is that the orignial comment can't be found/seen
		# by third parties using various 'undelete' methods
		permalink = praw_comment.permalink
		footer = _report_bug.format(permalink=permalink) + _FEEDBACK + _SOURCE_CODE
		deleted_comment = "[Deleted by OP's request]\n\n***\n\n" + footer
		praw_comment.edit(deleted_comment)
		self._logger.info("deleted comment")
