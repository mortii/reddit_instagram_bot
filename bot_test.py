#using pytest
from redditInstagramBot import *

def testing_link_filter():
	#**this assumes a working internet connection and sampled working link still working**

	#dead link, should return empty list
	links = ['https://www.instagram.com/p/-sBbhIKIEUrgrgrg/'] 
	assert filter_dead_links(links) == []

	#[dead link, working link], should return one link
	links = ['https://www.instagram.com/p/-sBbhIKIEUrgrgrg/', 'https://www.instagram.com/p/BCLjKLsiPOb/']
	assert filter_dead_links(links) == ['https://www.instagram.com/p/BCLjKLsiPOb/']

def testing_link_detection():
	#**this assumes a working internet connection and sampled links still working**

	# empty text returns empty lst
	text = ""
	assert get_insta_links(text) == []

	#should return three links
	text = """https://www.instagram.com/p/BCLjKLsiPOb/ 
	https://www.instagram.com/p/-sBbhIKIEU/ 
	https://www.instagram.com/p/BFlzDnjsSOx/"""
	assert get_insta_links(text) == ['https://www.instagram.com/p/-sBbhIKIEU/', 'https://www.instagram.com/p/BCLjKLsiPOb/', 'https://www.instagram.com/p/BFlzDnjsSOx/'] 

	#duplicates should get removed
	text = """https://www.instagram.com/p/BCLjKLsiPOb/ 
	https://www.instagram.com/p/-sBbhIKIEU/ 
	https://www.instagram.com/p/BFlzDnjsSOx/
	https://www.instagram.com/p/BFlzDnjsSOx/
	https://www.instagram.com/p/BFlzDnjsSOx/"""
	assert get_insta_links(text) == ['https://www.instagram.com/p/-sBbhIKIEU/', 'https://www.instagram.com/p/BCLjKLsiPOb/', 'https://www.instagram.com/p/BFlzDnjsSOx/'] 

	#more than 5 unique links should return empty list
	text = """https://www.instagram.com/p/BCLjKLsiPOb/ 
	https://www.instagram.com/p/-sBbhIKIEU/ 
	https://www.instagram.com/p/BFlzDnjsSOx/
	https://www.instagram.com/p/BFMv_QbuEay/
	https://www.instagram.com/p/BFmd6-vOEYi/
	https://www.instagram.com/p/BFmWzRFM95G/"""
	assert get_insta_links(text) == []
