# Author: Hao Lyu, UT Austin
# Run the script: Python crawl_hist_tweets.py example_input.csv output.csv
# Run the check mode: Python crawl_hist_tweets.py example_input.csv output.csv -check
# Search based on example_input.csv and generate output.csv file in the same folder
import requests
import sys
import operator
import os.path
from bs4 import BeautifulSoup
from Queue import Queue
import random
import time
import csv
import check_missed_data 

input_file = sys.argv[1]
output_file = sys.argv[2]

# Load the data 
data = {}
data['tweet_id'] = []
data['author_full_name'] = []
csv.field_size_limit(sys.maxsize)

with open(input_file,'r') as f:
	r = csv.DictReader(f)
	fieldnames = r.fieldnames
	for row in r:
		data['tweet_id'].append(row[fieldnames[0]])
		data['author_full_name'].append(row[fieldnames[1]])

test_number = len(data['author_full_name'])
count = Queue()

for i in range(test_number):	
	count.put(i)

recorded_dict = {}
error_list = []

# Load the output file
if not os.path.isfile(output_file):
	with open(output_file,'a+') as o:
		output_keys = ['tweet_id','author_full_name','hist_list']
		w = csv.DictWriter(o, output_keys)
		w.writeheader()
else:
	with open(output_file,'rb') as o:
		r = csv.DictReader(o)
		for row in r:
			recorded_dict[row['author_full_name']] = 1

# Push the data into a queue
queue = Queue()

for i in range(test_number):	
	one_doc = [data['tweet_id'][i], 
				data['author_full_name'][i]
				]
	if one_doc[1] in recorded_dict:
		continue
	else:
		queue.put_nowait(one_doc)

# Login Twitter
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
#proxies = {"https":"https://186.229.16.154:80",
#			"http":"http://107.151.142.115:80"
#			}

headers = {
			'Host': 'twitter.com',
			'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.11; rv:43.0) Gecko/20100101 Firefox/43.0',
			'Accept': 'application/json, text/javascript, */*; q=0.01',
			'Accept-Language': 'en-US,en;q=0.5',
			'Accept-Encoding': 'gzip, deflate',
			'X-Requested-With': 'XMLHttpRequest',
			"Cookie": "guest_id=v1%3A142982010899019442; _ga=GA1.2.513563793.1452280674; dnt=1; remember_checked_on=1; webn=4729798346; _twitter_sess=BAh7CiIKZmxhc2hJQzonQWN0aW9uQ29udHJvbGxlcjo6Rmxhc2g6OkZsYXNo%250ASGFzaHsABjoKQHVzZWR7ADoPY3JlYXRlZF9hdGwrCMYhRDlSAToMY3NyZl9p%250AZCIlNjAwZTgyMDc3MThmNmZhODg1OTA5Zjg5ZGZhMDYyMWM6B2lkIiU0YjY0%250AN2RlMDFlYWM2ZGU4ZjgwY2VjMjY0ZWU5OWZiOToJdXNlcmwrCMr%252B6hkBAA%253D%253D--2df9ca19a7a75ca949a2f50b20fc000b21c61cef; lang=en; kdt=CraZVP9NO2TVAdEcyUYkqUPTKgcLfQ03IilYsiVG; ua=\'f5,m2,m5,msw\'; _gat=1; twid=\'u=4729798346\';auth_token=545FAB363CF7AAA2F49492111432B01C5613DE48; _gat=1",
			'Connection': 'keep-alive'}

# Crawl one user's tweet using its name
def single_crawler(key):
	global recorded_dict
	global error_list

	tweet_id = key[0]
	user_screen_name = key[1]

	if user_screen_name in recorded_dict:
		return 

	hist_list = []
	request_times = 0
	
	try:
		# Extract the tweets in the homepage of the user
		get_url = "http://twitter.com/" + user_screen_name 
		p = requests.get(get_url, headers=headers)			
		soup = BeautifulSoup(p.content,  "lxml")
		jstt = soup.find("div", {"id": "timeline"}).find("div", {"class": "stream-container  "})
		start_position = str(jstt['data-min-position'])
		new_jstt = soup.find("div", {"id": "timeline"}).find_all("p")

		for one in new_jstt:
			hist_list.append(one.text)

		# Repetitively crawl user historical tweets and extract them
		while(start_position != None):
			if request_times >= 20:
				request_times = 0
				sleep_time = random.randint(1,4)
				time.sleep(sleep_time)

			one_url = 'http://twitter.com/i/profiles/show/' + user_screen_name + '/timeline?include_available_features=1&include_entities=1&last_note_ts=123&max_position=' + start_position + '&reset_error_state=false'
			params = {
					'include_available_features': '1',
					'include_entities': '1',
					'max_position': start_position, 
					'reset_error_state': 'false',
					'last_note_ts': 123
					}

			response = requests.get(one_url, params=params, headers=headers)
			request_times += 1
			fixtures =  response.json()

			if 'inner' in fixtures.keys():
				fixtures = (response.json())['inner']

			start_position = fixtures['min_position']
			soup2 = BeautifulSoup(fixtures['items_html'], "lxml")
			jstt2 = soup2.find_all("p", {"lang": "en"})

			for one_fol in jstt2:
				hist_list.append(one_fol.text)

			if len(hist_list)>999:
				break
				
		print "No %d user %s inputs %d tweets:" %(count.get_nowait(), user_screen_name, len(hist_list))		
		output_keys = data.keys()+['hist_list']	

		with open(output_file,'a') as o:
			w = csv.DictWriter(o, output_keys)
			w.writerow({'tweet_id':tweet_id, 
		    				'author_full_name':user_screen_name,
		    				'hist_list': hist_list
		    				})
		
		recorded_dict[user_screen_name] = 1

	except Exception,e:
		error_list.append(key)
		print 'error in crawling author %s'%(user_screen_name)
		return
	
	return

def crawl_all_data():
	wait_times = 0
	while(not(queue.empty())):
		wait_times += 1
		if wait_times%5 == 0:
			sleep_time = random.randint(1,4)
			time.sleep(sleep_time)

		single_crawler(queue.get_nowait())

def check_error_data():
	wait_times = 0
	max_try_times = 3*len(error_list)

	while(len(error_list)>0):
		wait_times += 1

		if wait_times > max_try_times:
			break
		if wait_times%5 == 0:
			sleep_time = random.randint(1,4)
			time.sleep(sleep_time)

		single_crawler(error_list.pop(0))
	print "There are %d authors who are not existed or protected"%(len(error_list))
	print "They are: "
	left_list = [names[1] for names in error_list]
	for name in left_list:
		print 'left_list',

try:
	if sys.argv[3] == '-check':
		missed_data = check_missed_data.check_missed_data(input_file, output_file)
		for key in missed_data:
			single_crawler(key)
		print 'error_list has %d authors'%(len(error_list))
		check_error_data()

	else:
		'Wrong arguments input, try again'

except IndexError:
	crawl_all_data()
	print 'error list has %d users'%(len(error_list))
	if len(error_list)!=0:
		print 'wait 1min and recrawl users in the error list'
		sleep_time = random.randint(50,90)
		time.sleep(sleep_time)
		check_error_data()
	else:
		print 'Work is done'

#Example
#single_crawler(['545163607366184960','ThisIsArtful'])
#single_crawler(['410439170067152896','RealJoshJacobs'])
