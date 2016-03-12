# Author: Hao Lyu, UT Austin
# Check if there are any missed users in the output.csv who are occuring in the input data
# Run by: Python check_missed_data.py data3.csv output.csv
import csv
import sys

def check_missed_data(data, output):
	missed = []
	data_dict = {}
	csv.field_size_limit(sys.maxsize)

	with open(output, 'r') as f:
		# ['tweet_id','author_full_name']
		r = csv.DictReader(f)
		for row in r:
			#data_dict[row['tweet_id']] = row['author_full_name']
			data_dict[row['author_full_name']] = row['tweet_id']

	with open(data, 'r') as f:
		# ['tweet_id','author_full_name']
		r = csv.DictReader(f)
		for row in r:
			#if row['tweet_id'] not in data_dict:
			if row['author_full_name'] not in data_dict:
				missed.append([row['tweet_id'],row['author_full_name']])

	return missed

if __name__ == '__main__':
	try:
		missed = check_missed_data(sys.argv[1], sys.argv[2])
		print "There are %d missed authors in %s compared with %s"%(len(missed), sys.argv[2], sys.argv[1])
	except IndexError:
		print 'require data and output on command line, type as: Python check_missed_data.py data.csv output.csv'
