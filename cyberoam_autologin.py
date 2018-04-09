import requests
import re
import random
import time
import logging

HOST_URL = 'http://172.16.0.30:8090/login.xml'
PASSWORD = "default_password"

def tryUserLogin(username,password):
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
credsDict = {'f2014855':'blackberry29!','f2013358':'Dreimar@123','f2013408':'pussycat123@'}

logging.basicConfig(filename='cyberoam_login_logging.log',level=logging.DEBUG,format='%(asctime)s %(message)s', datefmt='%m/%d/%Y %I:%M:%S %p')

def runLoginScript():
	while(1):
    		try:
	    	# Randomly pick usernames and distribute load
        		random_username = random.choice(list(credsDict.keys()))
	        	pwd = credsDict[random_username]
			print random_username
			logging.info('Chosen username = '+random_username)
			try:
		        	message = tryUserLogin(random_username,pwd)
				logging.debug(message)
		            	if(message == '<![CDATA[You have successfully logged in]]>'):
		                	print('Logged In As ' + random_username)
			                break
				else:
		                	if(message == '<![CDATA[Your data transfer has been exceeded, Please contact the administrator]]>'):
		                    		print('Connection Failed for '+username+' Data Limit has already exceeded.')
		                	if(message == '<![CDATA[The system could not log you on. Make sure your password is correct]]>'):
		                    		print('Connection Failed for '+username+' due to incorrect password.')
		                	num=num+1
		            		time.sleep(3)
			except:
				# Exhausted our list and couldn't log in
				logging.error("End of list reached. Couldn't log in :(. Supply new usernames and passwords")
				break
		except:
			# Network error
		        #print("Login failed due to network error. Please try again.")
			logging.critical("Login failed due to network error. Please try again.")
	
if __name__=='__main__':
	runLoginScript()
	
