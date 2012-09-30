from BeautifulSoup import BeautifulSoup
import urllib2
import time
import os
import random
import cPickle as pickle

def init():
	try:
		forum_pkl = open('data/forum_store.pkl', 'rb')
		forum_ids = pickle.load(forum_pkl)
		forum_pkl.close()
	except:
		forum_pkl, forum_ids = None, []
	return forum_ids

def save(forum_ids):
	try:
		forum_pkl = open('data/forum_store.pkl', 'wb')
		pickle.dump(forum_ids, forum_pkl)
		forum_pkl.flush()
		forum_pkl.close()
	except:
		print "ERROR: Unable to pickle forum_store."
	return

def findLimit():
	core_url = "http://forum.419eater.com/forum/"
	page_name = "viewforum.php"
	forum_args = "?f=18&start="
	page_increment = 0
	while True:
		try:
			current_page = urllib2.urlopen(core_url + page_name + forum_args + str(page_increment))
		except:
			return 300
		soup = BeautifulSoup(current_page)
		count = 0
		for link in soup.findAll('a', href=True):
			if 'viewtopic.php' in link['href']:
				if count > 7:
					break
				count += 1
		if count == 7:
			break
		page_increment += 30
	return page_increment - 30  # adjust for final, empty page


def crawlIndex(limit=270):
	links = []
	exceptions = ['188427', '105921', '190170', '176248']  # administrative topics
	core_url = "http://forum.419eater.com/forum/"
	page_name = "viewforum.php"
	forum_args = "?f=18&start="
	page_increment = 0
	while page_increment <= limit:
		try:
			current_page = urllib2.urlopen(core_url + page_name + forum_args + str(page_increment))
		except:
			print "Failing on:", core_url + page_name + forum_args + str(page_increment)
		soup = BeautifulSoup(current_page)
		for link in soup.findAll('a', href=True):
			if 'viewtopic.php' in link['href']:
				try:
					link_id = link['href'].split('&')[0].split('=')[1]
					if link_id not in links and str(link_id) not in exceptions:
						links.append(str(link_id))
				except:
					print "Problem in link separation"
		page_increment += 30
	return list(set(links) - set(exceptions))


def crawlPost(link_id):
	exceptions = ['ipTRACKERonline.com']
	core_url = "http://forum.419eater.com/forum/"
	page_name = "viewtopic.php"
	forum_args = "?t="
	response = None
	try:
		post = urllib2.urlopen(core_url + page_name + forum_args + link_id)
		soup = BeautifulSoup(post, convertEntities=BeautifulSoup.HTML_ENTITIES)
		try:  # hating BeautifulSoup
			response = soup.findAll("td", {"class": "postbody"})[1]
			response = response.renderContents()
			for elem in exceptions:
				if elem in response:
					return None
			response = response.replace('<br />\n<br />\n', '<magic>\n')
			response = response.replace('<br />\n', '')
			response = response.replace('<magic>\n', '<br />\n')
			response = BeautifulSoup(response)
			response = response.findAll(text=True)
			response = ''.join(response)
			response = response.encode('ascii', 'ignore')
			response = response.replace('\r\n ', '\r\n')
			response = response.replace('\n\n  Quote:   ', '')
		except:
			return None
	except:
		print "Failing on:", core_url + page_name + forum_args + link_id
	return response  # WARNING: Unicode


def crawlAndWrite(links):
	forum_ids = init()
	module_id = 'CRAWLER'
	base = os.environ['HOME'] + '/dev/proj/incoming/' + module_id + '-'
	for link_id in links:
		response = crawlPost(link_id)
		if response and str(link_id) not in forum_ids:
			tmp_name = base + str(link_id) + '.tmp'
			final_name = base + str(link_id) + '.ready'
			fileh = open(tmp_name, 'w')
			fileh.write(response)
			fileh.flush()
			fileh.close()
			os.rename(tmp_name, final_name) # Atomic
			forum_ids.append(str(link_id))
	save(forum_ids)
	return

def go():
	crawlAndWrite(crawlIndex(findLimit()))
	return

if __name__ == "__main__":
	while True:
		try:
			print "Crawling..."
			go()
			idle = random.choice(range(10, 35)) * 100
			print "Waiting %d secs." % (idle)
			time.sleep(idle)
		except Exception, e:
			print "Caught exception:", e
