import os

FACEBOOK_CLIENT_ID = os.environ.get('FACEBOOK_CLIENT_ID')
FACEBOOK_CLIENT_SECRET =  os.environ.get('FACEBOOK_CLIENT_SECRET')

FACEBOOK_TOKEN_EXCHANGE_URI = "https://graph.facebook.com/oauth/access_token?grant_type=fb_exchange_token&client_id=%s&client_secret=%s&fb_exchange_token=%s"

GITHUB_CLIENT_ID = os.environ.get('GITHUB_CLIENT_ID')
GITHUB_CLIENT_SECRET =  os.environ.get('GITHUB_CLIENT_SECRET')

INSTAGRAM_CLIENT_ID = os.environ.get('INSTAGRAM_CLIENT_ID')
INSTAGRAM_CLIENT_SECRET = os.environ.get('INSTAGRAM_CLIENT_SECRET')
INSTAGRAM_REDIRECT_URI = os.environ.get('INSTAGRAM_REDIRECT_URI')

FOURSQUARE_CLIENT_ID = os.environ.get('FOURSQUARE_CLIENT_ID')
FOURSQUARE_CLIENT_SECRET = os.environ.get('FOURSQUARE_CLIENT_SECRET')
FOURSQUARE_REDIRECT_URI = os.environ.get('FOURSQUARE_REDIRECT_URI')