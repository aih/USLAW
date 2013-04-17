# Post to twit
from oauth import oauth
from oauthtwitter import OAuthApi
from local_settings import consumer_key, consumer_secret, access_token, access_token_secret

def post_message(message):
    #  TODO: add some tests
    twitter = OAuthApi(consumer_key, consumer_secret, access_token, access_token_secret)
    twitter.UpdateStatus(message)
    return True

