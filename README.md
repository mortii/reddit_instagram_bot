# Bot Task:
This bot searches through new submissions and comments in selected subreddits and when it finds one or more instagram links the bot then replies with a mirror of the instagram post(s).


### Example 1:
<p align="center"><b>(Closed)</b></p>

<p align="center">
  <img src="http://i.imgur.com/0hMBaTY.png"/>
</p>

<p align="center"><b>(Opened)</b></p>

<p align="center">
  <img src="http://i.imgur.com/wzmpnFt.png"/>
</p>

### Example 2:
<p align="center"><b>(Closed)</b></p>

<p align="center">
  <img src="http://i.imgur.com/KsWflRL.png"/>
</p>

<p align="center"><b>(Opened)</b></p>

<p align="center">
  <img src="http://i.imgur.com/DLDJrTa.png"/>
</p>

### Hosting:
This bot is hosted on the Heroku, hence the requirements.txt, Procfile, and storing sensitive data as environment variables.

### Requirements:
* Python 2.7.10
* beautifulsoup (bs4)
* requests
* imgurpython
* praw
* prawoauth2
