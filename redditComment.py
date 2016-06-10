from instagramScraper import Instagram


comment_footer = ("^I'm ^a ^bot. [^[Report ^Bug]]"
	"(https://np.reddit.com/message/compose/?to=bestme&amp;subject=InstagramMirror%20bug)"
	"[^[Give ^Feedback ^or ^Suggestions]]"
	"(https://np.reddit.com/message/compose/?to=bestme&amp;subject=InstagramMirror%20feedback/suggestion)"
	"[^[Source ^Code]](https://github.com/mortii/reddit_instagram_bot)")


def create_comment(insta_links):
	total_comment = "" 

	for link in insta_links:
		total_comment += insta_post(link)
	total_comment += comment_footer

	if len(total_comment) >= 10000:
		total_comment = "Sorry, caption(s) too long for a reddit comment.\n\n***\n\n'" + comment_footer
	return total_comment


def insta_post(link):
	insta = Instagram(link)
	header = '[**%s(%s):**](%s)' % (insta.title, insta.user, insta.url)
	time = '\n\n>^(%s)' % insta.time
	media_mirror = "\n\n>[[%s Mirror]](%s)" % (insta.media, insta.mirror_url)
	caption = '\n\n>%s\n\n***\n\n' % insta.caption

	insta_post = header + time + media_mirror + caption
	return insta_post