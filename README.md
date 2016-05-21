## Bot Task:
This bot searches through new submissions and comments for instagram links in selected subreddits. When an instagram link is found the bot then replies with a mirror of the instagram post(s).

### Examples:
![](http://i.imgur.com/MAjsI1P.png "single link")

<p align="center">
  <img src="http://iconizer.net/files/IconSweets/orig/arrow_down.png"/>
</p>

![](http://i.imgur.com/UXojmXq.png "single link opened")

***

![](http://i.imgur.com/wiOnWeV.png "multiple links")

<p align="center">
  <img src="http://iconizer.net/files/IconSweets/orig/arrow_down.png"/>
</p>

![](http://i.imgur.com/mNiwXJ7.png "multiple links opened")


###Hosting:
This bot is hosted on Heroku, hence the requirements.txt, Procfile, and storing the tokens and client details as environment variables.

	
###Dependencies:
* beautifulsoup (bs4)
* imgurpython
* praw
* prawoauth2

