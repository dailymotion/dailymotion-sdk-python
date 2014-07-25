This is the python SDK for using Dailymotion Graph API V3.

INSTALL
-------

Install dailymotion module

    $ python setup.py install

Install pycurl

    $ pip install pycurl


Install requests

    $ pip install requests

To run tests
    
    $ pip install nose
    $ nosetests -v


DEBUG
-----


EXAMPLE
-------

```python
d = dailymotion.Dailymotion()
d.set_grant_type('password', api_key=API_KEY, api_secret=API_SECRET, scope=['manage_videos', 'manage_comments'], info={'username': USERNAME, 'password': PASSWORD})
d.get('/videos', )
```
