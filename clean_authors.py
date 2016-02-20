# Check whether the author's Twitter homepage exists
# Update a field 'exist' to each author. 0 means 'not exist', 1 means 'exist'
import requests
import sys
import operator
from bs4 import BeautifulSoup
from pymongo import MongoClient
import datetime
from multiprocessing import Process, Queue
from multiprocessing import Pool
import random
import time
# Load the data into mongodb
client = MongoClient('127.0.0.1', 27017)
db = client['IronyHQ']
dbtweets = db.tweets
test_number =  dbtweets.find({'$and':[{'hist_list' : {'$exists': False}}, {'exist' : {'$exists': False}}]}).count()


#test_number = dbtweets.find({'hist_list' : {'$exists': False}}).count()

print 'total left empty authors count is: ', test_number
count = Queue()
#for i in range(dbtweets.find({'hist_list' : {'$exists': False}}).count()):
for i in range(test_number):	
	count.put(i)


queue = Queue()


#for i in range(dbtweets.find({'hist_list' : {'$exists': False}}).count()):
for i in range(test_number):	
	try:
		one_doc = [dbtweets.find({'$and':[{'hist_list' : {'$exists': False}}, {'exist' : {'$exists': False}}]})[i]['tweet_id'], 
					dbtweets.find({'$and':[{'hist_list' : {'$exists': False}}, {'exist' : {'$exists': False}}]})[i]['author_full_name']
					]

		#print "this is No.%d" %i + " Doc: ", one_doc
		queue.put_nowait(one_doc)
		#print one_doc
	except Exception:
		continue



url = "https://twitter.com/login"
payload = { 'session[username_or_email]': 'irony_research', 
			'session[password]': 'research_irony'
			}

# two more accounts

#payload1 = { 'session[username_or_email]': 'irony_research1', 
#			'session[password]': 'research1_irony'
#			}

#payload2 = { 'session[username_or_email]': 'irony_research2', 
#			'session[password]': 'research2_irony'
#			}

r = requests.post(url, data=payload)

proxies = {
	
	"http": "http://192.99.54.110:80",
	"http": "http://192.99.54.41:8080", 
	"http": "http://207.96.132.67:80",
	"http": "http://216.113.14.15:8000",
	"http": "http://50.30.152.130:8086"
	
}


headers = [{
			'Host': 'twitter.com',
			'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.11; rv:43.0) Gecko/20100101 Firefox/43.0',
			'Accept': 'application/json, text/javascript, */*; q=0.01',
			'Accept-Language': 'en-US,en;q=0.5',
			'Accept-Encoding': 'gzip, deflate',
			'X-Requested-With': 'XMLHttpRequest',
			"Cookie": "guest_id=v1%3A142982010899019442; _ga=GA1.2.513563793.1452280674; dnt=1; remember_checked_on=1; webn=4729798346; _twitter_sess=BAh7CiIKZmxhc2hJQzonQWN0aW9uQ29udHJvbGxlcjo6Rmxhc2g6OkZsYXNo%250ASGFzaHsABjoKQHVzZWR7ADoPY3JlYXRlZF9hdGwrCMYhRDlSAToMY3NyZl9p%250AZCIlNjAwZTgyMDc3MThmNmZhODg1OTA5Zjg5ZGZhMDYyMWM6B2lkIiU0YjY0%250AN2RlMDFlYWM2ZGU4ZjgwY2VjMjY0ZWU5OWZiOToJdXNlcmwrCMr%252B6hkBAA%253D%253D--2df9ca19a7a75ca949a2f50b20fc000b21c61cef; lang=en; kdt=CraZVP9NO2TVAdEcyUYkqUPTKgcLfQ03IilYsiVG; ua=\'f5,m2,m5,msw\'; _gat=1; twid=\'u=4729798346\';auth_token=545FAB363CF7AAA2F49492111432B01C5613DE48; _gat=1",
			'Connection': 'keep-alive'},
			{
			'Host': 'twitter.com',
			'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.11; rv:43.0) Gecko/20100101 Firefox/43.0',
			'Accept': 'application/json, text/javascript, */*; q=0.01',
			'Accept-Language': 'en-US,en;q=0.5',
			'Accept-Encoding': 'gzip, deflate',
			'X-Requested-With': 'XMLHttpRequest',
			"Cookie": "guest_id=v1%3A142982010899019442; _ga=GA1.2.513563793.1452280674; dnt=1; remember_checked_on=1; webn=4729798346; _twitter_sess=BAh7CiIKZmxhc2hJQzonQWN0aW9uQ29udHJvbGxlcjo6Rmxhc2g6OkZsYXNo%250ASGFzaHsABjoKQHVzZWR7ADoPY3JlYXRlZF9hdGwrCMYhRDlSAToMY3NyZl9p%250AZCIlNjAwZTgyMDc3MThmNmZhODg1OTA5Zjg5ZGZhMDYyMWM6B2lkIiU0YjY0%250AN2RlMDFlYWM2ZGU4ZjgwY2VjMjY0ZWU5OWZiOToJdXNlcmwrCMr%252B6hkBAA%253D%253D--2df9ca19a7a75ca949a2f50b20fc000b21c61cef; lang=en; kdt=CraZVP9NO2TVAdEcyUYkqUPTKgcLfQ03IilYsiVG; ua=\'f5,m2,m5,msw\'; _gat=1; twid=\'u=4809014914\';auth_token=6A2CD516E37E2D66CC8B6B79D5A35307E5916FA2; _gat=1",
			'Connection': 'keep-alive'},
			{
			'Host': 'twitter.com',
			'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.11; rv:43.0) Gecko/20100101 Firefox/43.0',
			'Accept': 'application/json, text/javascript, */*; q=0.01',
			'Accept-Language': 'en-US,en;q=0.5',
			'Accept-Encoding': 'gzip, deflate',
			'X-Requested-With': 'XMLHttpRequest',
			"Cookie": "guest_id=v1%3A142982010899019442; _ga=GA1.2.513563793.1452280674; dnt=1; remember_checked_on=1; webn=4729798346; _twitter_sess=BAh7CiIKZmxhc2hJQzonQWN0aW9uQ29udHJvbGxlcjo6Rmxhc2g6OkZsYXNo%250ASGFzaHsABjoKQHVzZWR7ADoPY3JlYXRlZF9hdGwrCMYhRDlSAToMY3NyZl9p%250AZCIlNjAwZTgyMDc3MThmNmZhODg1OTA5Zjg5ZGZhMDYyMWM6B2lkIiU0YjY0%250AN2RlMDFlYWM2ZGU4ZjgwY2VjMjY0ZWU5OWZiOToJdXNlcmwrCMr%252B6hkBAA%253D%253D--2df9ca19a7a75ca949a2f50b20fc000b21c61cef; lang=en; kdt=CraZVP9NO2TVAdEcyUYkqUPTKgcLfQ03IilYsiVG; ua=\'f5,m2,m5,msw\'; _gat=1; twid=\'u=4808934921\';auth_token=0DA3357AC77D39E2BC73FD0F481E61750A6DED36; _gat=1",
			'Connection': 'keep-alive'}]
# set start time
start_time = datetime.datetime.now()

def foo(key):
	print '***************'
	#print 'test_count %d' % test_count
	client_no = random.randint(0,2)
	tweet_id = key[0]
	user_screen_name = key[1]

	try:
		get_url = "https://twitter.com/" + user_screen_name 
		p = requests.get(get_url, headers=headers[client_no], proxies=proxies)
			
		soup = BeautifulSoup(p.content,  "lxml")
		jstt = soup.find("div", {"id": "timeline"}).find("div", {"class": "stream-container  "})
		start_position = str(jstt['data-min-position'])
		new_jstt = soup.find("div", {"id": "timeline"}).find_all("p")
			
		result = dbtweets.update_one({"tweet_id": tweet_id},
					{
					    "$set": {
			                "exist": 1
			        	}
					}
				)
			
	except AttributeError:
		result = dbtweets.update_one({"tweet_id": tweet_id},
					{
					    "$set": {
			                "exist": 0
			        	}
					}
				)
		return
	except Exception,e:
		print 'type %s and text %s and author is %s'%(type(e), e, user_screen_name)
		return
	
	return

def many_foos():
	wait_times = 0
	while(not(queue.empty())):
		wait_times += 1
		if wait_times%50 == 0:
			sleep_time = random.randint(1,4)
			time.sleep(sleep_time)
		foo(queue.get_nowait())


many_foos()
end_time = datetime.datetime.now()
duration = end_time - start_time
print " total time is ", duration
