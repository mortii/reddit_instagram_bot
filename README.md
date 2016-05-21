## Bot Task:
This bot searches through new submissions and comments in selected subreddits and when it finds one or more instagram links the bot then replies with a mirror of the instagram post(s).

###Example 1:
<p align="center"><b>(Closed)<b></p>

<p align="center">
  <img src="http://i.imgur.com/MAjsI1P.png"/>
</p>

<p align="center"><b>(Opened)<b></p>

<p align="center">
  <img src="http://i.imgur.com/UXojmXq.png"/>
</p>

###Example 2:

<p align="center"><b>(Closed)<b></p>

<p align="center">
  <img src="http://i.imgur.com/wiOnWeV.png"/>
</p>

<p align="center"><b>(Opened)<b></p>

<p align="center">
  <img src="http://i.imgur.com/mNiwXJ7.png"/>
</p>


###Hosting:
This bot is hosted on Heroku, hence the requirements.txt, Procfile, and storing the tokens and client details as environment variables.

	
###Dependencies:
* beautifulsoup (bs4)
* imgurpython
* praw
* prawoauth2
