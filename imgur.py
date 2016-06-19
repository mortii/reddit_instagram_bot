import os
from imgurpython import ImgurClient


client_id = os.environ['client_id']
client_secret = os.environ['client_secret']
imgur_client = ImgurClient(client_id, client_secret)


def upload_picture(picture_url):
	dictionary = imgur_client.upload_from_url(picture_url, config=None, anon=False)
	imgur_url = dictionary["link"] 
	return imgur_url