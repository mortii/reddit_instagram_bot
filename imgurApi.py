from imgurpython import ImgurClient
from secrets import client_id, client_secret

client = ImgurClient(client_id, client_secret)

def upload_picture(pic_url):
	dic = client.upload_from_url(pic_url, config=None, anon=False)
	return dic["link"]