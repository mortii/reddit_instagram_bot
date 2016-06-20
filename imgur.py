import os
from imgurpython import ImgurClient


_client_id = os.environ['client_id']
_client_secret = os.environ['client_secret']
_imgur_client = ImgurClient(_client_id, _client_secret)


def upload_picture(pic_url):
	dictionary = _imgur_client.upload_from_url(pic_url, config=None, anon=False)
	imgur_url = dictionary["link"]
	return imgur_url
