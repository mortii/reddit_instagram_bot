import requests


def upload_vid(video_url):
	response = requests.get('https://api.streamable.com/import?url=' + video_url)
	dictionary = response.json()
	shortcode = dictionary['shortcode']
	streamable_url = get_streamable_url(shortcode) 
	return streamable_url


def get_streamable_url(shortcode):
	response = requests.get('https://api.streamable.com/videos/' + shortcode)
	dictionary = response.json()
	streamable_url = "https://www." + dictionary['url'] 
	return streamable_url