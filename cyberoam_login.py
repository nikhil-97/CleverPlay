'''
Forked from repo akhilrb/cyberoam-autologin
'''

import requests
import re
import random
import time

HOST_URL = 'host_url'
USERNAME_LIST = []
CHOICE = ''
PASSWORD = "default_password"

def tryUser(username,password):
    try:
            a_param = str(int(time.time()*1000))
            credentials = {'mode':'191','username':username,'password':password,'a':a_param}
            post_response = requests.post(HOST_URL,data = credentials)
            postData = post_response.content
            message = re.findall(r'<message>(.*?)</message>',str(postData))
            return message[0]
        
    except (requests.ConnectionError,requests.HTTPError) as err:
            print(str(err))

num = 0
# Make a temporary list of the Usernames
tempList = username


while(1):
    try:
        # Randomly pick usernames and distribute load
        choice = random.choice(tempList)

        try:
            message = tryUser(username,password)
            if(message == '<![CDATA[You have successfully logged in]]>'):
                print('Logged In As ' + username)
                break
            else:
                if(message == '<![CDATA[Your data transfer has been exceeded, Please contact the administrator]]>'):
                    print('Connection Failed for user %s. Data Limit has already exceeded.'%(username))
                if(message == '<![CDATA[The system could not log you on. Make sure your password is correct]]>'):
                    print('Connection Failed for user %s due to incorrect password.'%(username))
                num=num+1
            # Pop incorrect choice from list
            tempList.remove(choice)
            # Optional time delay
            time.sleep(3)
        except:
            # Exhausted our list and couldn't log in
            print("End of list reached. Couldn't log in :(")
            break
    except:
        # Network error
        print("Login failed due to network error. Please try again.")
