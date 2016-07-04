import requests


def upload_video(video_url):
	response = requests.get('https://api.streamable.com/import?url=' + video_url)
	dictionary = response.json()
	shortcode = dictionary['shortcode']
	streamable_url = _get_streamable_url(shortcode)
	return streamable_url


def _get_streamable_url(shortcode):
	response = requests.get('https://api.streamable.com/videos/' + shortcode)
	dictionary = response.json()
	streamable_url = "https://" + dictionary['url']
	return streamable_url
