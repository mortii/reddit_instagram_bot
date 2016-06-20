import json
import urllib2 as urllib
import re as regex

from bs4 import BeautifulSoup

import streamable
import imgur


class Instagram:
	def __init__(self, url):
		url_reader = urllib.urlopen(url)
		soup = BeautifulSoup(url_reader, 'html.parser')
		self.url = url
		self.user = self._get_user(soup)
		self.title, self.time = self._get_title_and_time(soup)
		self.caption = self._get_caption(soup)
		self.pic_url = self._get_pic_url(soup)
		self.vid_url = self._get_vid_url(soup)

		if self.vid_url is not None:
			self.media = 'Video'
			self.mirror_url = streamable.upload_video(self.vid_url)
		else:
			self.media = 'Image'
			self.mirror_url = imgur.upload_picture(self.pic_url)

	def _get_user(self, soup):
		tag = soup.findAll("meta", {"content": regex.compile(r'@')})
		for tag_attributes in tag:
			content = tag_attributes.get('content')
			user = self._slice_user(content)
			return user

	def _slice_user(self, content):
		begin = content.find("@")
		content = content[begin:]
		end = content.find(" ")
		user = content[:end]
		return user

	def _get_title_and_time(self, soup):
		tag = soup.findAll("meta", {"content": regex.compile(r'.UTC')})
		for tag_attributes in tag:
			content = tag_attributes.get("content")
			content = self._remove_default_name(content)
			title, time = self._slice_title_and_time(content)
			return title, time

	def _remove_default_name(self, content):
		# done in order to avoid having '@username' twice in the mirror header
		has_default_name = content.find('by @')
		if has_default_name != -1:
			content = content.replace("by @", "by ")
		return content

	def _slice_title_and_time(self, text):
		DATETIME_PATTERN = r'[a-zA-Z]+\s[\d]+,\s20[\d]{2}\sat\s[\d:pmam]+\sUTC'
		reg = regex.search(DATETIME_PATTERN, text)
		time_start = reg.start()
		title = text[:time_start - 2]
		time = text[time_start:]
		return title, time

	def _get_caption(self, soup):
		all_text = str(soup)
		window_data = self._get_window_data(all_text)
		rough_caption = self._get_json_caption(window_data)
		caption = self._clean_caption(rough_caption)
		return caption

	def _get_window_data(self, all_text):
		WINDOW_START_PATTERN = r'<script type="text/javascript">window._sharedData'
		WINDOW_END_PATTERN = r'};</script>'
		reg_start = regex.search(WINDOW_START_PATTERN, all_text)
		reg_end = regex.search(WINDOW_END_PATTERN, all_text)
		begin = reg_start.start() + 52
		end = reg_end.start() + 1
		window_data = all_text[begin:end]
		return window_data

	def _get_json_caption(self, window_data):
		window_data = json.loads(window_data)
		for post in window_data['entry_data']['PostPage']:
			try:
				return post['media']['caption']
			except KeyError:
				return ""

	def _clean_caption(self, rough_caption):
		caption = regex.sub(r'#', r'\#', rough_caption)
		caption = regex.sub(r'\n', r'\n\n>', caption)
		caption = regex.sub(r'\"', r'"', caption)
		return caption

	def _get_pic_url(self, soup):
		tag = soup.findAll("meta", {"content": regex.compile(r'.jpg\?')})
		for pic_url in tag:
			return pic_url.get("content")

	def _get_vid_url(self, soup):
		tag = soup.findAll("meta", {"content": regex.compile(r'.mp4')})
		for vid_url in tag:
			return vid_url.get("content")
