from bs4 import BeautifulSoup
import json
import urllib2 as urllib
import re
import unicodedata
import streamable
import imgur


class Instagram:
	def __init__(self, url):
		url_reader = urllib.urlopen(url)
		soup = BeautifulSoup(url_reader, 'html.parser')
		self.user = self.get_user(soup)
		self.title, self.time = self.get_title_and_time(soup)
		self.caption = self.get_caption(soup)
		self.url = url
		self.vid_url = self.get_vid_url(soup)
		self.pic_url = self.get_pic_url(soup)

		if self.vid_url == None:
			self.media = 'Image'
			self.mirror_url = imgur.upload_picture(self.pic_url)
		else:
			self.media = 'Video'
			self.mirror_url = streamable.upload_video(self.vid_url)

			
	def get_user(self, soup):
		tag = soup.findAll("meta", {"content" : re.compile(r'@')})
		for tag_attributes in tag:
			content = tag_attributes.get('content')
			user = self.slice_user(content)
			return user


	def slice_user(self, content):
		begin = content.find("@")
		content = content[begin:]
		end = content.find(" ")
		user = content[:end]
		return user


	def get_title_and_time(self, soup):
		tag = soup.findAll("meta", {"content" : re.compile(r'.UTC')})
		for tag_attributes in tag:
			content = tag_attributes.get("content")
			content = self.remove_default_name(content)
			title, time = self.slice_title_and_time(content)
			return title, time


	def remove_default_name(self, content):
		#done in order to avoid having '@username' twice in the mirror header
		has_default_name = content.find('by @')
		if has_default_name != -1:
			content = content.replace("by @", "by ")
		return content


	def slice_title_and_time(self, text):
		reg = re.search(r'[a-zA-Z]+\s[\d]+,\s20[\d]{2}\sat\s[\d:pmam]+\sUTC', text)
		time_start = reg.start()
		title = text[:time_start-2] 
		time = text[time_start:]
		return title, time


	def get_caption(self, soup):
		all_text = str(soup)
		window_text = self.slice_text(all_text)
		rough_caption = self.get_json_caption(window_text)
		caption = self.clean_caption(rough_caption)
		return caption

		
	def slice_text(self, all_text):
		reg_start = re.search(r'<script type="text/javascript">window._sharedData', all_text)
		reg_end = re.search(r'};</script>', all_text)
		begin =  reg_start.start() + 52
		end = reg_end.start() + 1
		window_text = all_text[begin : end]
		return window_text	


	def get_json_caption(self, window_text):
		window_text = json.loads(window_text)
		for post in window_text['entry_data']['PostPage']:
			try:
				return post['media']['caption']
			except:
				return ""


	def clean_caption(self, rough_caption):
		caption = re.sub(r'#', r'\#', rough_caption)
		caption = re.sub(r'\n', r'\n\n>', caption)
		caption = re.sub(r'\"', r'"', caption)
		return caption


	def get_pic_url(self, soup):
		tag = soup.findAll("meta", {"content" : re.compile(r'.jpg?')})
		for pic_url in tag:
			return pic_url.get("content")


	def get_vid_url(self, soup):
		tag = soup.findAll("meta", {"content" : re.compile(r'.mp4')})
		for vid_url in tag:
			return vid_url.get("content")