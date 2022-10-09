import os
import json
import time
import tweepy
import pandas as pd
import operator
import random
import regex as re
from urllib.request import urlopen
from tweepy.cursor import Cursor
from Auth.oauth import Oauth
import textblob as textblob

def cleantext(text):
    text = re.sub(r'@[A-Za-z0-9]+','' ,text)
    text = re.sub(r'#','',text)
    text = re.sub(r'RT[\s]+','',text)
    text = re.sub(r'https?:\/\/\S+','', text)

    return text

def getsubjectivity(text):
    return textblob.TextBlob(text).sentiment.subjectivity

def getpolarity(text):
    return textblob.TextBlob(text).sentiment.polarity

def tweet_analysis(score):
    if score < 0:
        return 'Negative'
    elif score == 0:
        return 'Neutral'
    else:
        return 'Positive'


def get_tweets_polarity(api,user):
    tweets = []
    tweets_polarity = {}
    tweets = api.user_timeline(user_id = user,count = 100,tweet_mode = "extended")
    for tweet in tweets:
        clean_tweet = cleantext(tweet.full_text)
        tweet_polarity = getpolarity(clean_tweet)
        tweet_sense = tweet_analysis(tweet_polarity)
        words = clean_tweet.split(" ")
        for word in words:
            if word not in tweets_polarity.keys():
                tweets_polarity[word] = tweet_sense

    return tweets_polarity

def get_matching_users(api, prime_user, users):

    prime_user_tweets_polarity = get_tweets_polarity(api,prime_user)
    final_users = []

    for user in users:
        count = 0
        user_tweets_polarity = get_tweets_polarity(api,user)
        for word in user_tweets_polarity:
            if word in prime_user_tweets_polarity:
                if user_tweets_polarity[word] == prime_user_tweets_polarity[word]:
                    count = count + 1
                if count == 50:
                    final_users.append(user)
                    break
    return final_users


def get_user_profile(api,screenName=None, userId=None):   
    return api.get_user(user_id = userId,screen_name = screenName)


def get_geo_users(api,cities,itr):
    geo_users = []
    depth = 1
    for i in cities:
        while depth <= itr:
            try:
                geo_users.extend(api.search_users(q = i, page = depth))
                print(len(geo_users))
            except tweepy.errors.TooManyRequests:
                print("Too many requests")
                time.sleep(1000)
            except tweepy.errors.Unauthorized:
                print("experencing 401 error")
            except tweepy.errors.TwitterServerError:
                print("experencing 503 error")
            except tweepy.errors.BadRequest:
                print("experencing 400 error")
            depth += 1
        depth = 1
    return geo_users


def filter_name_geo(geo_user,cities,csv_path,excel_path):
    #working_dir = str(os.path.abspath(os.path.dirname(os.path.dirname(__file__))))
    #working_dir = working_dir.replace("\\","/")
    #firstname_file = working_dir + '/SSA_Names_DB.xlsx'
    #lastname_file = working_dir + '/Common_Surnames_Census_2000.csv'
    #last_name = pd.read_csv(r'')
    #first_name = pd.read_excel(working_dir + '/SSA_Names_DB.xlsx')
    last_name = pd.read_csv(r'{0}'.format(csv_path))
    first_name = pd.read_excel(r'{0}'.format(excel_path))
    last_name_users = pd.DataFrame(last_name, columns = ['name'])
    first_name_users = pd.DataFrame(first_name, columns = ['Name'])

    geo_user_name_filtered = []
    geo_dump = []
    for city in range(len(cities)):
        for user in range(len(geo_user)):
            if cities[city].casefold() in geo_user[user].name.casefold():
                geo_dump.append(geo_user[user])

    for user in geo_user:
        if user not in geo_dump:
            fields = user.name.split(" ")
            if len(fields) == 3 or len(fields) == 2:
                user_first = fields[0]
                user_second = fields[1]
                if user_first in first_name_users.values:
                    if user_second.upper() in last_name_users.values:
                        geo_user_name_filtered.append(user)
            else:
                user_first = fields[0]
                if user_first.upper() in first_name_users.values:
                    geo_user_name_filtered.append(user)

    return geo_user_name_filtered


def filter_gender(api,screen_name):
    myKey = "BB8Gl8Nu3dPWzG2NNVLPSeko5hsFlcabCo5T"

    main_user = api.get_user(screen_name = screen_name)
    first_name = main_user.name.split(" ")[0]

    url = "https://gender-api.com/get?key=" + myKey + "&name=" + first_name.upper()
    response = urlopen(url)
    decoded = response.read().decode('utf-8')
    data = json.loads(decoded)
    main_user_gender = data["gender"]

    return 'male' if main_user_gender == 'female' else 'female'


def filter_friends(api,users,my_user,retry=0,dict_user = {},no_friends_list = []):
    print("\n*******************------------------****************\n")
    try:
        print("Finding friends for : ",my_user.screen_name)
        user_friends = set(api.get_friend_ids(screen_name = my_user.screen_name))
        print("my user friends :", len(user_friends))
        
        #for page in Cursor(api.get_friend_ids,screen_name = my_user.screen_name).pages():
        #    print("current page :",page)
        #    user_friends |= set(page)
        #    print(len(page))

        count = 0
        index = 0
        prev_index = -1
        while index <len(users):
            if prev_index == index:
                count += 1                
                
            try:
                prev_index = index
                print("Finding friends for",users[index]['user_screen_name'])
                friends_list = set(api.get_friend_ids(screen_name = users[index]['user_screen_name']))
                print("User:", users[index]['user_screen_name'], "friends count :",len(friends_list))
                dict_user[users[index]['user_id']] = len(user_friends&friends_list)
                print("User Dict",dict_user)
                print(dict_user)
                index += 1
            except tweepy.errors.TooManyRequests:
                if count >6:
                    print("No Friends for",users[index]['user_screen_name'])
                    no_friends_list.append(users[index])
                    index +=1
                api = Oauth(index%6).oauth()
                print("Using key hash:",index%6)
            except Exception:
                no_friends_list.append(users[index])
                index +=1
                            
    except tweepy.errors.TooManyRequests:
        if retry > 8:
            print("Requests across all keys timed out ! Waiting for rate limit refresh...")
            retry = 0
            time.sleep(900)
        retry = retry + 1
        api = Oauth(retry%6).oauth()
        print("Changed to key hash:", retry%6)
        print("Retry Count",retry)
        filter_friends(api,users,my_user,retry,dict_user,no_friends_list)
    except tweepy.errors.Unauthorized:
        print("experencing 401 error")
    except tweepy.errors.TwitterServerError:
        print("experencing 503 error")
    except tweepy.errors.BadRequest:
        print("experencing 400 error")
    except tweepy.errors.NotFound:
        print("experencing 404 error")
    except Exception as e:
        print(e)
        
    print("no friends for:",len(no_friends_list))
    print(dict(sorted(dict_user.items(), key=operator.itemgetter(1), reverse=True)[:10]))
    #dict_user = {k: v for k, v in sorted(dict_user.items(), key=lambda item: item[1], reverse = True)}
    #result = dict(sorted(dict_user.items(), key=operator.itemgetter(1), reverse=True)[:10]).keys()
    #result = result if result not {} else random.sample(user_friends,10)def 
    # filter gender
    return dict(sorted(dict_user.items(), key=operator.itemgetter(1), reverse=True)[:10]).keys()
