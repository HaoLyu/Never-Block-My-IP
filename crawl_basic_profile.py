# Author: Hao Lyu, UT Austin
# Run the script: Python crawl_basic_profile.py example_input.csv output_basic_profile.csv
# Search based on example_input.csv and generate output_basic_profile.csv file in the same folder
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
import string
import datetime
import re
from geopy import geocoders

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
		output_keys = ['tweet_id', 'author_full_name', 'following_count', 'followers_count',
						'profile', 'duration', 'verified', 'avg_tweet', 'time_zone']
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

# remove punctuation in string
regex = re.compile('[%s]' % re.escape(string.punctuation))

# number convert '100,5K'->1005000
def num_convert(val):
	try:
		if (('K' not in val)&('M' not in val)&('B' not in val)):
			return float(regex.sub('', val))
		val_1 = regex.sub('.', val)
		lookup = {'K': 1000, 'M': 1000000, 'B': 1000000000}
		unit = val_1[-1]
		try:
			number = float(val_1[:-1])
		except ValueError:
			print 'number is wrong: ',val
			return -1
		if unit in lookup:
			return lookup[unit] * number
		return float(val_1)
	except ValueError:
		print 'number is wrong: ',val
		return -1

# time convert 'Joined October 2009' -> datetime.datetime(2009, 10, 1, 0, 0)
def date_convert(s):
	date_string = s.split('-')[1].strip()
	date = datetime.datetime.strptime(date_string, '%d %b %Y')

	return date

# check timezone of the user. Limits: 2000queries/24h 
def time_zone_check(s):
	try:
		g = geocoders.GoogleV3()	
		place, (lat, lng) = g.geocode(s)
		return_p = place.encode('utf-8').strip()
		return return_p.split(',')[-1].strip()
	except:
		return ''

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
	request_times = 0
	
	try:
		get_url = "http://twitter.com/" + user_screen_name 
		p = requests.get(get_url, headers=headers)			
		soup = BeautifulSoup(p.content,  "lxml")
		# Extract the tweets user has sent
		jstt = soup.find("li", {"class": "ProfileNav-item ProfileNav-item--tweets is-active"}).find("span", {"class": "ProfileNav-value"})
		tweets_count = str(jstt.get_text())
		tweets_count = num_convert(tweets_count)

		# Extract the number of following 
		jstt = soup.find("li", {"class": "ProfileNav-item ProfileNav-item--following"}).find("span", {"class": "ProfileNav-value"})
		following_count = str(jstt.get_text())
		following_count = num_convert(following_count)

		# Extract the number of followers
		jstt = soup.find("li", {"class": "ProfileNav-item ProfileNav-item--followers"}).find("span", {"class": "ProfileNav-value"})
		followers_count = str(jstt.get_text())
		followers_count = num_convert(followers_count)

		# Extract the profile of the user
		jstt = soup.find("p", {"class": "ProfileHeaderCard-bio u-dir"})
		profile = jstt.get_text().encode('ascii','ignore')

		# Extract how long has the user used Twitter
		jstt = soup.find("div", {"class": "ProfileHeaderCard-joinDate"}).find("span", {"class": "ProfileHeaderCard-joinDateText js-tooltip u-dir"})["title"]
		join_time = str(jstt)
		join_time_convert = date_convert(join_time)
		current_time = datetime.datetime.now()
		duration = (current_time - join_time_convert).days
		
		# Extract the verification of the user
		jstt = soup.find("h1", {"class": "ProfileHeaderCard-name"}).find("span", {"class": "ProfileHeaderCard-badges ProfileHeaderCard-badges--1"})
		verified = str(jstt)
		if verified is not None:
			verified = 'yes'
		else:
			verified = 'no'

		# average tweets/day
		avg = tweets_count/float(duration)

		# # Extract the time zone of the user
		jstt = soup.find("div", {"class": "ProfileHeaderCard-location"}).find("span", {"class": "ProfileHeaderCard-locationText u-dir"})
		time_zone = time_zone_check(str(jstt.text).strip()).strip()
		if len(time_zone) < 1:
			time_zone = 'None'

		output_keys = ['tweet_id', 'author_full_name', 'following_count', 'followers_count',
						'profile', 'duration', 'verified', 'avg_tweet', 'time_zone']	

		with open(output_file,'a') as o:
			w = csv.DictWriter(o, output_keys)
			w.writerow({'tweet_id':tweet_id, 
		    				'author_full_name': user_screen_name,
		    				'following_count': following_count,
		    				'followers_count': followers_count,
		    				'profile': profile, 
		    				'duration': duration, 
		    				'verified': verified, 
		    				'avg_tweet': avg,
		    				'time_zone': time_zone
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



