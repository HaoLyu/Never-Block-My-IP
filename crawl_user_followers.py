# Author: Hao Lyu, UT Austin
# Run the script: Python crawl_basic_profile.py example_input.csv output_user_followers.csv
# Search based on example_input.csv and generate output_user_followers.csv file in the same folder
import requests
import sys
import operator
import os.path
from bs4 import BeautifulSoup
from Queue import Queue
import random
import time
import csv
import urllib
import re
import string
import datetime
import re
import json
import string

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
		output_keys = ['tweet_id', 'author_full_name', 'followers_list']
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
	global error_list
	tweet_id = key[0]
	user_screen_name = key[1]

	followers_list = []
	request_times = 0
	
	try:
		get_url = "https://twitter.com/" + user_screen_name + "/followers"
		p = requests.get(get_url, headers=headers)			
		soup = BeautifulSoup(p.content,  "lxml")
		jstt = soup.find("div", {"class": "GridTimeline"}).find("div", {"class": "GridTimeline-items"})

		start_position = str(jstt['data-min-position'])
		first_jstt = soup.find_all("a",{"class":"ProfileCard-screennameLink u-linkComplex js-nav"})
		for one in first_jstt:
			insert = (one.text).strip().replace('@','').encode('utf-8')
			followers_list.append(insert)

		while(start_position != '0'):
			one_url = 'https://twitter.com/' + user_screen_name + '/followers/users?include_available_features=1&include_entities=1&max_position=' + start_position + '&reset_error_state=false'
			params = {
					'include_available_features': '1',
					'include_entities': '1',
					'max_position': start_position, 
					'reset_error_state': 'false'
					}
			response = requests.get(one_url, params=params, headers=headers)
			fixtures = response.json()
			start_position = fixtures['min_position']
			soup2 = BeautifulSoup(fixtures['items_html'], "lxml")
			jstt2 = soup2.find_all("div", {"class": "ProfileCard  js-actionable-user"})

			for one_fol in jstt2:
				followers_list.append(one_fol['data-screen-name'].encode('utf-8'))
			
			# Default the number of max followers is 999
			if len(followers_list)>999:
				break

		output_keys = ['tweet_id', 'author_full_name', 'followers_list']	
		with open(output_file,'a') as o:
			w = csv.DictWriter(o, output_keys)
			w.writerow({'tweet_id':tweet_id, 
		    				'author_full_name': user_screen_name,
		    				'followers_list': followers_list
		    				})

	except Exception,e:
		print 'type %s and text %s and author is %s'%(type(e), e, user_screen_name)
		error_list.append(key)
		return
	
	return

def crawl_all_data():
	wait_times = 0
	while(not(queue.empty())):
		wait_times += 1
		if wait_times%50 == 0:
			sleep_time = random.randint(1,4)
			time.sleep(sleep_time)

		single_crawler(queue.get_nowait())

def check_error_data():
	wait_times = 0

	while(len(error_list)>0):
		wait_times += 1
		if wait_times%50 == 0:
			sleep_time = random.randint(1,4)
			time.sleep(sleep_time)

		single_crawler(error_list.pop())

	print "There are %d authors who are not existed or protected"%(len(error_list))
	print "They are: "
	left_list = [names[1] for names in error_list]

	for name in left_list:
		print 'left_list',

# Example input		
#single_crawler(['545163607366184960','ThisIsArtful'])
#single_crawler(['410439170067152896','RealJoshJacobs'])

crawl_all_data()
print 'error list has %d users'%(len(error_list))
if len(error_list)!=0:
		print 'wait 1min and recrawl users in the error list'
		sleep_time = random.randint(50,90)
		time.sleep(sleep_time)
		check_error_data()
else:
	print 'Work is done'

