import os

CLIENT_ID = os.getenv('DM_CLIENT_ID', '[YOUR API KEY]')
CLIENT_SECRET = os.getenv('DM_CLIENT_SECRET', '[YOUR API SECRET]')
USERNAME = os.getenv('DM_USERNAME', '[YOUR USERNAME]')
PASSWORD = os.getenv('DM_PASSWORD', '[YOUR PASSWORD]')
REDIRECT_URI = os.getenv('DM_REDIRECT_URI', '[YOUR REDIRECT URI]')
BASE_URL = 'https://api.dailymotion.com'
OAUTH_AUTHORIZE_URL = 'https://www.dailymotion.com/oauth/authorize'
OAUTH_TOKEN_URL = 'https://api.dailymotion.com/oauth/token'
