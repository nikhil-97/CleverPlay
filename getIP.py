import socket
import requests
import cyberoam_autologin
from time import sleep

def getIPaddress():
	s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
	s.connect(("8.8.8.8", 80))
	ip = s.getsockname()[0]
	print(ip)
	query_args={'IP':str(ip)}
	response = requests.post(url= "http://www.findmysport.in/getIP.php", params = query_args)
	print "response = ", response
	print response.url
	s.close()

cyberoam_autologin.runLoginScript()
sleep(2)
getIPaddress()


