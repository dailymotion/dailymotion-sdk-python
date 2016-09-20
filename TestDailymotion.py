import dailymotion
import unittest
import config
import re
import time
import os

class TestA(unittest.TestCase):

    @classmethod
    def setUpClass(self):
        self.api_base_url                   = config.BASE_URL or 'http://api.dailymotion.com'
        self.api_key                        = config.CLIENT_ID
        self.api_secret                     = config.CLIENT_SECRET
        self.username                       = config.USERNAME
        self.password                       = config.PASSWORD
        self.scope                          = ['manage_videos', 'manage_playlists', 'userinfo']
        self.redirect_uri                   = config.REDIRECT_URI
        self.oauth_authorize_endpoint_url   = config.OAUTH_AUTHORIZE_URL or 'https://api.dailymotion.com/oauth/authorize'
        self.oauth_token_endpoint_url       = config.OAUTH_TOKEN_URL or 'https://api.dailymotion.com/oauth/token'
        self.session_file_directory  = './data'
        if not os.path.exists(self.session_file_directory):
            os.makedirs(self.session_file_directory)

    @classmethod
    def tearDownClass(self):
        if os.path.exists(self.session_file_directory):
            os.rmdir(self.session_file_directory)

    def test_init(self):
        d = dailymotion.Dailymotion()
        self.assertEqual(d.api_base_url, 'https://api.dailymotion.com')

        d = dailymotion.Dailymotion(api_base_url='http://api.stage.dailymotion.com', timeout=10, debug=True)
        self.assertEqual(d.api_base_url, 'http://api.stage.dailymotion.com')
        self.assertEqual(d.timeout, 10)
        self.assertEqual(d.debug, True)

    def test_get(self):
        d = dailymotion.Dailymotion()
        videos = d.get('/videos')
        self.assertEqual('has_more' in videos, True)
        self.assertEqual(videos['has_more'], True)
        self.assertEqual('list' in videos, True)
        self.assertEqual(len(videos['list']) > 0, True)

    def test_set_grant_type(self):
        d = dailymotion.Dailymotion()
        self.assertRaises(dailymotion.DailymotionClientError, d.set_grant_type, 'password', api_secret=self.api_secret, scope=self.scope,
            info={'username': self.username, 'password': self.password})
        self.assertRaises(dailymotion.DailymotionClientError, d.set_grant_type, 'password', api_secret=self.api_secret, scope=self.scope)
        self.assertRaises(dailymotion.DailymotionClientError, d.set_grant_type, 'password', api_secret=self.api_secret, scope=None)

    def test_get_authorization_url(self):
        d = dailymotion.Dailymotion(api_base_url=self.api_base_url, oauth_authorize_endpoint_url=self.oauth_authorize_endpoint_url)
        d.set_grant_type('authorization', api_key=self.api_key, api_secret=self.api_secret, scope=self.scope, info={'redirect_uri' : self.redirect_uri})
        authorization_url = d.get_authorization_url(redirect_uri=self.redirect_uri, scope=self.scope)
        self.assertEqual(re.match('https?://(?:www)?(?:[\w-]{2,255}(?:\.\w{2,6}){1,2})(?:/[\w&%?#-]{1,300})?',authorization_url) == None, False)

    def test_get_access_token(self):
        d = dailymotion.Dailymotion(api_base_url=self.api_base_url,
                                oauth_authorize_endpoint_url=self.oauth_authorize_endpoint_url,
                                oauth_token_endpoint_url=self.oauth_token_endpoint_url)
        d.set_grant_type('password', api_key=self.api_key, api_secret=self.api_secret, scope=self.scope, info={'username': self.username, 'password': self.password})
        access_token = d.get_access_token()
        self.assertEqual(isinstance (access_token, str) or isinstance(access_token, unicode), True)
        d.logout()

    def test_set_access_token(self):
        d = dailymotion.Dailymotion()
        d.set_grant_type('password', api_key=self.api_key, api_secret=self.api_secret, scope=self.scope, info={'username': self.username, 'password': self.password})
        d.set_access_token(d.get_access_token())
        response = d.get('/me/?fields=fullname')
        self.assertEqual(isinstance (response.get('fullname'), str) or isinstance(response.get('fullname'), unicode), True)
        d.logout()

    def test_auth_call(self):
        d = dailymotion.Dailymotion(api_base_url=self.api_base_url,
                                oauth_authorize_endpoint_url=self.oauth_authorize_endpoint_url,
                                oauth_token_endpoint_url=self.oauth_token_endpoint_url,
                                session_store_enabled=True)

        d.set_grant_type('password', api_key=self.api_key, api_secret=self.api_secret, scope=self.scope, info={'username': self.username, 'password': self.password})
        response = d.get('/me/?fields=fullname')
        self.assertEqual(isinstance (response.get('fullname'), str) or isinstance(response.get('fullname'), unicode), True)
        d.logout()

    def test_upload(self):
        d = dailymotion.Dailymotion(api_base_url=self.api_base_url,
                                oauth_authorize_endpoint_url=self.oauth_authorize_endpoint_url,
                                oauth_token_endpoint_url=self.oauth_token_endpoint_url,
                                session_store_enabled=True)

        d.set_grant_type('password', api_key=self.api_key, api_secret=self.api_secret, scope=self.scope, info={'username': self.username, 'password': self.password})
        url = d.upload('./examples/video.mp4')
        self.assertEqual(re.match('https?://(?:www)?(?:[\w-]{2,255}(?:\.\w{2,6}){1,2})(?:/[\w&%?#-]{1,300})?',url) == None, False)
        d.post('/videos', {'url' : url,
                            'title' : 'my_test_upload_%s' % time.strftime("%c"),
                            'published' : 'true',
                            'channel' : 'news'
                        })
        d.logout()


    def test_session_store_option(self):
        d = dailymotion.Dailymotion(session_store_enabled=False)
        self.assertFalse(d._session_store_enabled)

        d = dailymotion.Dailymotion(session_store_enabled=True)
        self.assertTrue(d._session_store_enabled)

        d = dailymotion.Dailymotion(session_store_enabled=None)
        self.assertEqual(d.DEFAULT_SESSION_STORE, d._session_store_enabled)

    def test_in_memory_session(self):
        d = dailymotion.Dailymotion(api_base_url=self.api_base_url,
                                oauth_authorize_endpoint_url=self.oauth_authorize_endpoint_url,
                                oauth_token_endpoint_url=self.oauth_token_endpoint_url,
                                session_store_enabled=True)
        d.set_grant_type('password', api_key=self.api_key, api_secret=self.api_secret, scope=self.scope, info={'username': self.username, 'password': self.password})
        access_token = d.get_access_token()
        self.assertEqual(isinstance (access_token, str) or isinstance(access_token, unicode), True)
        second_access_token = d.get_access_token()
        self.assertEqual(isinstance (second_access_token, str) or isinstance(second_access_token, unicode), True)
        self.assertEqual(second_access_token, access_token)
        d.logout()

    def test_file_storage_session(self):
        fs = dailymotion.FileSessionStore(self.session_file_directory)
        d = dailymotion.Dailymotion(api_base_url=self.api_base_url,
                                oauth_authorize_endpoint_url=self.oauth_authorize_endpoint_url,
                                oauth_token_endpoint_url=self.oauth_token_endpoint_url,
                                session_store_enabled=True,
                                session_store=fs)
        d.set_grant_type('password', api_key=self.api_key, api_secret=self.api_secret, scope=self.scope, info={'username': self.username, 'password': self.password})
        access_token = d.get_access_token()
        self.assertEqual(isinstance (access_token, str) or isinstance(access_token, unicode), True)
        second_access_token = d.get_access_token()
        self.assertEqual(isinstance (second_access_token, str) or isinstance(second_access_token, unicode), True)
        self.assertEqual(second_access_token, access_token)
        d.logout()
