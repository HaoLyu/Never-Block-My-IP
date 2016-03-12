##Never-Block-My-IP

Twitter Crawler coded with Python

##What you can get

* Historical tweets/timeline
* Number of followings/followers
* Name list of followers
* Profile
* Usage time duration on Twitter
* Avg tweet per day

##Installing

```
Note: You will need at least Python 2.7 and several Python libraries including geopy, bs4, and requests.
If you get into any problem, please send an email to lyuhao@utexas.edu
```

To use the code, git clone the repository first 

```
> git clone https://github.com/HaoLyu/Never-Block-My-IP.git
> cd Never-Block-My-IP
```

##Example of usage

To run crawler on raw text input with tweet_id,author_full_name per line (e.g. on the
sample_input.txt):

Extract timeline tweets of users
```
> python crawl_hist_tweets.py example_input.txt output.csv 
```

The output file will be "output.csv" in the same directory as
"sample_input.txt".

Other usage
```
> python crawl_basic_profile.py example_input.txt output_basic_profile.csv 
> python crawl_user_followers.py example_input.txt output_user_followers.csv 
```

