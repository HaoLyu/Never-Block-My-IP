# Crawle free proxy ips from the first 10 pages of http://www2.waselproxy.com/
# Build a ip_pool 
import requests
from bs4 import BeautifulSoup

class IP_spider(object):
	def __init__(self):
		self.ip_pool = []
		pass
	def generate_ip_pool(self):		
		for page in range(1,11):
			get_url = "http://www2.waselproxy.com/page/" + str(page)
			p = requests.get(get_url)					
			soup = BeautifulSoup(p.content,  "lxml")
			ip_row = soup.find_all("tr")

			for one in ip_row[1:]:
				try:
					x = one.find("progress")
					value = int(x.get('value'))

					if value >= 50:
						content = (one.text).encode('utf-8')
						ip_context = content.strip().split('\n')
						ip = "http://" + ip_context[0] + ":" + ip_context[1]
						self.ip_pool.append(ip)

				except Exception:
					continue
		return self.ip_pool
if __name__ == '__main__':
	foo = IP_spider()
	x = foo.generate_ip_pool()
	print len(x)
	print x
