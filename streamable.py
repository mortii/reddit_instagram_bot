import requests


def upload_vid(url):
	r = requests.get('https://api.streamable.com/import?url=' + url)
	dic = r.json()
	shortcode = dic['shortcode']
	return retrieve_url(shortcode)


def retrieve_url(shortcode):
	link = 'https://api.streamable.com/videos/' + shortcode
	r = requests.get(link)
	dic = r.json()
	return "https://www." + dic['url']