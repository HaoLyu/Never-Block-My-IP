# process
# requests model
import requests
import sys
import operator
from bs4 import BeautifulSoup
from pymongo import MongoClient
import datetime
from Queue import Queue
import random
import time
import proxy_ip_spider as ipSpider
# Build a ip_pool
IPs = ipSpider.IP_spider()
ip_pool = IPs.generate_ip_pool()

# Load the data into mongodb
client = MongoClient('127.0.0.1', 27017)
db = client['IronyHQ']
dbtweets = db.tweets
#test_number = 3000
test_number = dbtweets.find({'$and':[{'exist' : 1},{'hist_list': {'$exists': False}}]}).count()

print 'total left empty authors count is: ', test_number
count = Queue()
#for i in range(dbtweets.find({'hist_list' : {'$exists': False}}).count()):
for i in range(test_number):	
	count.put(i)
recorded_dict = {}
error_list = []

for i in range(dbtweets.find({'hist_list' : {'$exists': True}}).count()):
	author_name = dbtweets.find({'hist_list' : {'$exists': True}})[i]['author_full_name']
	if author_name in recorded_dict:
		continue
	else:
		recorded_dict[author_name] = 1

queue = Queue()


for i in range(dbtweets.find({'exist' : {'$exists': False}}).count()):	
	one_doc = [dbtweets.find({'exist' : {'$exists': False}})[i]['tweet_id'], 
				dbtweets.find({'exist' : {'$exists': False}})[i]['author_full_name']
				]
	if one_doc[1] in recorded_dict:
		continue
	else:
		queue.put_nowait(one_doc)

for i in range(dbtweets.find({'exist' : 1}).count()):	
	try:
		one_doc = [dbtweets.find({'exist' : 1})[i]['tweet_id'], 
					dbtweets.find({'exist' : 1})[i]['author_full_name']
					]
		if one_doc[1] in recorded_dict:
			continue

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

proxies = {"https":"http://157.7.130.246:8080",
			"http":"http://:202.50.176.212:8080"
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

 
test_count = 0

def foo(key):
	#print '***************'
	global test_count
	global recorded_dict
	global error_list
	global proxies
	#print 'test_count %d' % test_count

	client_no = random.randint(0,2)
	tweet_id = key[0]
	user_screen_name = key[1]
	if user_screen_name in recorded_dict:
		#print "this author %s has existed"%(user_screen_name)
		return 

	recorded_dict[user_screen_name] = 1

	hist_list = []
	request_times = 0
	
	try:
		get_url = "https://twitter.com/" + user_screen_name 
		p = requests.get(get_url, headers=headers[client_no])#, proxies=proxies)
			
		soup = BeautifulSoup(p.content,  "lxml")

		jstt = soup.find("div", {"id": "timeline"}).find("div", {"class": "stream-container  "})
		#print jstt['data-min-position']

		start_position = str(jstt['data-min-position'])
		#print start_position
		#print "No %d user %s is under inputing %s :" %(test_count+1, user_screen_name, str(f_count))
		new_jstt = soup.find("div", {"id": "timeline"}).find_all("p")
		for one in new_jstt:
			hist_list.append(one.text)

		while(start_position != None):
			if request_times >= 5:
				request_times = 0
				sleep_time = random.randint(1,4)
				time.sleep(sleep_time)
			one_url = 'https://twitter.com/i/profiles/show/' + user_screen_name + '/timeline?include_available_features=1&include_entities=1&last_note_ts=123&max_position=' + start_position + '&reset_error_state=false'
			params = {
					'include_available_features': '1',
					'include_entities': '1',
					'max_position': start_position, 
					'reset_error_state': 'false',
					'last_note_ts': 123
					}

			response = requests.get(one_url, params=params, headers=headers[client_no])#, proxies=proxies)
			request_times += 1
			#xxxx =  response.json()
			#print xxxx.keys()
			fixtures =  response.json()
			if 'inner' in fixtures.keys():
				fixtures = (response.json())['inner']
			start_position = fixtures['min_position']
			#latent_count = fixtures['new_latent_count']
			#lc += int(latent_count)
			#print 'lc is:', lc
			#print start_position
			#print fixtures['items_html']
			soup2 = BeautifulSoup(fixtures['items_html'], "lxml")
			jstt2 = soup2.find_all("p", {"lang": "en"})
			for one_fol in jstt2:
				#print one_fol.text
				hist_list.append(one_fol.text)

			if len(hist_list)>999:
				break
				
		test_count += 1
		print "No %d user %s inputed %d:" %(count.get_nowait(), user_screen_name, len(hist_list))
		#print "hist_list is :", hist_list		
		result = dbtweets.update_one({"tweet_id": tweet_id},
					{
					    "$set": {
			                "hist_list": hist_list
			        	}
					}
				)
	
		
	except KeyError:
		sleep_time = random.randint(10,30)
		time.sleep(sleep_time)
		error_list.append(user_screen_name)
		print 'add to error_list No.%d %s'%(len(error_list),user_screen_name)
		return
	except ValueError:
		sleep_time = random.randint(10,30)
		time.sleep(sleep_time)
		error_list.append(user_screen_name)
		print 'add to error_list No.%d %s'%(len(error_list),user_screen_name)
		return
	except Exception,e:
		print 'type %s and text %s and author is %s'%(type(e), e, user_screen_name)
		return
	
	return

def many_foos():
	wait_times = 0
	while(not(queue.empty())):
		one_ip = ip_pool[random.randint(0,len(ip_pool)-1)]
		#proxies = {"http":one_ip}

		wait_times += 1
		if wait_times%5 == 0:
			sleep_time = random.randint(1,4)
			time.sleep(sleep_time)

		foo(queue.get_nowait())

def many_error_foos():
	wait_times = 0
	while(len(error_list)>0):
		one_ip = ip_pool[random.randint(0,len(ip_pool))]
		#proxies = {"http":one_ip}

		wait_times += 1
		if wait_times%5 == 0:
			sleep_time = random.randint(1,4)
			time.sleep(sleep_time)

		foo(error_list.pop())
	
"""
process_num = 4

p = Pool(process_num)
for i in range(process_num):
	p.apply_async(many_foos, args=())
p.close()
p.join()
"""
many_foos()
print 'error list has %d authors'%(len(error_list))
sleep_time = random.randint(50,90)
time.sleep(sleep_time)
many_error_foos()


end_time = datetime.datetime.now()
duration = end_time - start_time

print " total time is ", duration
