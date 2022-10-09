import tweepy
from .keyhash import Hash
from .keys import Keys

class Oauth:
    def __init__(self,num):
        self.index = num

    def oauth(self):
        next_auth = 'hash'+str(self.index)
        for h in Hash:
            if h.name == next_auth:
                print(h.name)
                consumer,oauth = h.value
        auth = tweepy.OAuthHandler(consumer[0],consumer[1])
        auth.set_access_token(oauth[0],oauth[1])
        return(tweepy.API(auth))
