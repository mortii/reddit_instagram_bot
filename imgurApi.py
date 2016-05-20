import os
from imgurpython import ImgurClient

client_id = os.environ['client_id']
client_secret = os.environ['client_secret']
client = ImgurClient(client_id, client_secret)

def upload_picture(pic_url):
	dic = client.upload_from_url(pic_url, config=None, anon=False)
	return dic["link"]
	