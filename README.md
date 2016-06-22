Dailymotion API SDK for Python
==================
[![Build Status](https://travis-ci.org/dailymotion/dailymotion-sdk-python.svg?branch=master)](https://travis-ci.org/dailymotion/dailymotion-sdk-python) [![Coverage Status](https://coveralls.io/repos/dailymotion/dailymotion-sdk-python/badge.svg?branch=master&service=github)](https://coveralls.io/github/dailymotion/dailymotion-sdk-python?branch=master)


Installation
------------

```
$ pip install dailymotion
```

Or

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

Set your own access_token (assuming your access_token is valide):

```python
d = dailymotion.Dailymotion
d.set_access_token(YOUR_ACCESS_TOKEN)
d.get('/me')
```

Authentication:
---------------

The Dailymotion API requires OAuth 2.0 authentication in order to access protected resources.

Contrary to most SDKs, the Dailymotion Python SDK implements lazy authentication, which means that no authentication request is sent as long as no data is requested from the API. At which point, two requests are sent back-to-back during the first request for information, one to authenticate and one to fetch the data.

Please note that the Dailymotion Python SDK also takes care of abstracting the entire OAuth flow, from retrieving, storing and using access tokens, to using refresh tokens to gather new access tokens automatically. You shouldn't have to deal with access tokens manually.

The session storage is enabled by default, you can disabled it by passing `session_store_enabled=false` to the constructor.

Access tokens are stored in memory by default, storing them in your OS files is recommended :

```python
import dailymotion

# The ./data directory
file_session = dailymotion.FileSessionStore('./data')
d = dailymotion.Dailymotion(session_storage=file_session)
....
```



Tests
-----

1.  Install dependencies:

    ```
    $ pip install -r requirements.txt
    ```

2.  Update the file named _config.py_ or set environment variables with the following content:

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
    $ py.test TestDailymotion.py
    ```
