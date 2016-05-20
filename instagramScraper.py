from bs4 import BeautifulSoup
import urllib2 as urllib
import re
import unicodedata
import streamableApi
import imgurApi

class Instagram:
	def __init__(self, url):
		url_reader = urllib.urlopen(url)
		soup = BeautifulSoup(url_reader, 'html.parser')
		self.user = self.get_user(soup)
		self.title, self.time = self.get_title_and_time(soup)
		self.text = self.get_text(soup)
		self.url = url
		self.vid_url = self.get_vid_url(soup)
		self.pic_url = self.get_pic_url(soup)

		if self.vid_url == None:
			self.media = 'Image'
			self.mirror_url = imgurApi.upload_picture(self.pic_url)
		else:
			self.media = 'Video'
			self.mirror_url = streamableApi.upload_vid(self.vid_url)
			
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

	def get_text(self, soup):
		for raw_text in soup.find_all(text=re.compile(r'\"caption\"')):
			rough_text = self.slice_text(raw_text)
			text = self.clean_text(rough_text)
			return text
		return ""
		
	def slice_text(self, text):
		reg = re.search(r'\",\s\"caption\":\s\"', text)
		begin =  reg.start() + 15
		reg = re.search(r'\",\s\"likes\":\s{', text)
		end = reg.start()
		return text[begin : end]

	def clean_text(self, rough_text):
		text = re.sub(r'\\n', r'\n\n>', rough_text)
		text = re.sub(r'\\"', r'"', text)
		text = text.decode('unicode-escape')
		return text

	def get_pic_url(self, soup):
		tag = soup.findAll("meta", {"content" : re.compile(r'.jpg?')})
		for pic_url in tag:
			return pic_url.get("content")

	def get_vid_url(self, soup):
		tag = soup.findAll("meta", {"content" : re.compile(r'.mp4')})
		for vid_url in tag:
			return vid_url.get("content")