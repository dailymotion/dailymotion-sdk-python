Dailymotion API SDK for Python.

Installation
------------

```
$ git clone git@github.com:dailymotion/dailymotion-sdk-python.git
$ cd dailymotion-sdk-python
$ python setup.py install
```


Examples
--------

Public API call:

```python
d = dailymotion.Dailymotion()
d.get('/videos')
```

Authenticated call:

```python
d = dailymotion.Dailymotion()
d.set_grant_type('password', api_key=API_KEY, api_secret=API_SECRET,
    scope=['userinfo'], info={'username': USERNAME, 'password': PASSWORD})
d.get('/me', {'fields': 'id,fullname'})
```

Video upload:

```python
d = dailymotion.Dailymotion()
d.set_grant_type('password', api_key=API_KEY, api_secret=API_SECRET,
    scope=['manage_videos'], info={'username': USERNAME, 'password': PASSWORD})
url = d.upload('./video.mp4')
d.post('/me/videos',
    {'url': url, 'title': 'MyTitle', 'published': 'true', 'channel': 'news'})
```


Tests
-----

1.  Install Nose:

    ```
    $ pip install nose
    ```

2.  Create a new file named _config.py_ with the following content:

    ```python
    CLIENT_ID = '[YOUR API KEY]'
    CLIENT_SECRET = '[YOUR API SECRET]'
    USERNAME = '[YOUR USERNAME]'
    PASSWORD = '[YOUR PASSWORD]'
    REDIRECT_URI = '[YOUR REDIRECT URI]'
    BASE_URL = 'https://api.dailymotion.com'
    OAUTH_AUTHORIZE_URL = 'https://www.dailymotion.com/oauth/authorize'
    OAUTH_TOKEN_URL = 'https://api.dailymotion.com/oauth/token'
    ```

3.  Run tests:

    ```
    $ nosetests -v
    ```
