import pymongo
import json
#from pymongo import MongoClient

class database:
    def __init__(self,db,collection):
        self.client = pymongo.MongoClient("mongodb+srv://tweetrimony:SMDMProj123@cluster0.ypbt0.mongodb.net/"
                                 "tweetrimony?retryWrites=true&w=majority")
        self.db = self.client[db]
        self.col = self.db[collection]
        
    def save_mongo(self,users):
        user_details = {}
        for i in users:
            user_details = {"user_id" : i.id,
                                "user_id_str" : i.id_str,
                                "user_name" : i.name,
                                "user_screen_name" : i.screen_name,
                                "user_location" : i.location,
                                "user_description" : i.description,
                                "user_follower_count": i.followers_count,
                                "user_friends_count" : i.friends_count,
                                "user_listed_count" : i.listed_count,
                                "user_count_creation" : i.created_at,
                                "user_fav_count" : i.favourites_count,
                                "user_statuses_count" :i.statuses_count,
                                "user_lang" : i.lang,
                                "user_profile_background_image_url" : i.profile_background_image_url,
                                "user_profile_image_url" : i.profile_image_url
                                }
                
            try:
                x = self.col.insert_one(user_details)
            except pymongo.errors.ServerSelectionTimeoutError:
                print("pymongo.errors.ServerSelectionTimeoutError")

    def load_mongo(self,id=None,return_cursor=False,
                    criteria=None, projection=None):
        if id is not None:
            return self.col.find_one({"user_id": id})
        
        if criteria is None:
            criteria = {}
    
        if projection is None:
            cursor = self.col.find(criteria)
        else:
            cursor = self.col.find(criteria, projection)
        
        if return_cursor:
            return cursor
        else:
            return [ item for item in cursor ]
        
    def delete_mongo(self,id=None,criteria=None):
        if id is not None:
            self.col.delete_one({"user_id": id})
        if criteria is not None:
            self.col.delete_many(criteria)
        
