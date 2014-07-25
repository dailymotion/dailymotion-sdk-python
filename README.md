This is the python SDK for using Dailymotion Graph API V3.

INSTALL
-------

Install dailymotion module

    $ python setup.py install


EXAMPLES
--------

Public api call

```python
d = dailymotion.Dailymotion()
d.get('/videos')
```

Authenticated call

```python
d = dailymotion.Dailymotion()
d.set_grant_type('password', api_key=API_KEY, api_secret=API_SECRET, scope=['userinfo'], info={'username': USERNAME, 'password': PASSWORD})
d.get('/me', {'fields' : 'id,fullname'})
```

Publish new video

```python
d = dailymotion.Dailymotion()
d.set_grant_type('password', api_key=API_KEY, api_secret=API_SECRET, scope=['manage_videos'], info={'username': USERNAME, 'password': PASSWORD})
url = d.upload('./video.mp4')
d.post('/me/videos', {'url' : url, 'title' : 'MyTitle', 'published' : 'true', 'channel' : 'news'})
```

TESTS
-----
1. Install Nose

    $ pip install nose

2. Create a new file _config.py_.

```python
CLIENT_ID = '[YOUR API KEY]'
CLIENT_SECRET = '[YOUR API SECRET]'
USERNAME = '[YOUR USERNAME]'
PASSWORD = '[YOUR PASSWORD]'
REDIRECT_URI = '[YOUR REDIRECT URI]'
BASE_URL = 'https://api.dailymotion.com'
OAUTH_AUTHORIZE_URL = 'https://api.dailymotion.com/oauth/authorize'
OAUTH_TOKEN_URL = 'https://api.dailymotion.com/oauth/token'
```

3. Run tests

    $ nosetests -v