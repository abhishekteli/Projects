from Mongo import mongo
from Auth.oauth import Oauth
from User.user_detail import *

if __name__ == "__main__":

    count = 0
    db = "tweetrimony"
    collection = "tweeterdata"
    
    screen_name = str(input("Enter the 'screenname' of the person to be matched: "))
    api = Oauth(0).oauth()
    my_user = get_user_profile(api,screenName = screen_name)
    if not my_user.location:
        my_user.profile_location = my_user.location = str(input("Enter your location detail | Eg: Syracuse: "))
        print("User location set, searching nearby...\n")
    #print(user)
    # Get the state of the user
    # Get nearby cities of the user
    users_gender = filter_gender(api,screen_name)
    if users_gender == 'female':
        my_user_gender = 'male'
    else:
        my_user_gender = 'female'

    print("FINDING MATCHES FOR")
    print("************************************************************************************************")
    print("User Name : {0}".format(my_user.name))
    print("User Screen name : {0}".format(screen_name))
    print("User gender : {0}".format(my_user_gender))
    print("User location : {0}".format(my_user.profile_location))
    print("************************************************************************************************")

    geo_users_dump = []
    csv_path = input("Input the path of Common_Surnames_Census_2000.csv: ")
    xls_path = input("Input the path of SSA_Names_DB.xlsx: ")
    # Preprocessed 
    places = ['Chicago', 'Houston', 'Dallas', 'Austin', 'Seattle', 'Denver', 'Las Vegas', 'Boston', 'Charlotte',
              'Nashville', 'Atlanta', 'Cleveland', 'Irvine', 'Buffalo', 'Yonkers']
    #geo_users_dump = get_geo_users(api,places,50)        
    #geo_users_name_filtered = filter_name_geo(geo_users_dump,places,csv_path,excel_path)
    #gender_users_filtered = filter_gender(api,geo_users_name_filtered,my_user.screen_name)
    #print(len(gender_users_filtered))
    mongo = mongo.database(db,collection);
    #users = mongo.load_mongo()
    #mongo.save_mongo(gender_users_filtered)

    users = mongo.load_mongo(criteria={'user_gender': users_gender})
    #print("Mongo Users1::",users)
    users = sorted(users, key=lambda item: item['user_friends_count'])
    #print("Mongo Users::",users)
    print("Mongo Users::",len(users))
    filtered_friends_ids = filter_friends(api,users[:100],my_user)
    print(len(filtered_friends_ids))
    print("----------")
    print(filtered_friends_ids)
    print("*************end")
    final_users = get_matching_users(api, my_user.id, filtered_friends_ids)
    if len(final_users) > 0 :
        print("\n{1} We found {0} matches for YOU!!!".format(len(final_users), my_user.name))
        print("Below are the matching profiles")
        for user in final_users:
            count = count + 1
            matching_user = get_user_profile(api,userId = user)
            print("{0}.USER : {1}".format(count,matching_user.name))
    else:
        print("Sorry!! No matching profiles found.")
    #for user in users:
    #    print(user['user_screen_name'])
    
