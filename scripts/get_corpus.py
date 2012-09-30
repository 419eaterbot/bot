from BeautifulSoup import BeautifulSoup
import urllib2
import os
import re


def crawlIndex(forum_id):
	threads = []
	prev_links, curr_links = [], []
	core_url = "http://antifraudintl.org/"
	page_name = "forumdisplay.php"
	forum_args = "?f=" + str(forum_id) + "&order=desc&page="
	page_increment = 1
	while True:
		try:
			print "Opening", core_url + page_name + forum_args + str(page_increment)
			current_page = urllib2.urlopen(core_url + page_name + forum_args + str(page_increment))
		except:
			print "Failing at", page_increment
			continue
		soup = BeautifulSoup(current_page)
		for link in soup.findAll('a', href=True):
			if 'showthread.php' in link['href']:
				try:
					link_id = int(link['href'].split('t=')[1])
					curr_links.append(link_id)
				except:
					pass
		if list(set(curr_links) - set(prev_links)) != []:
			page_increment += 1
			prev_links = curr_links
			threads.extend(curr_links)
			curr_links = []
		else:
			break
	return list(set(threads))


def crawlPost(link_id):
	core_url = "http://antifraudintl.org/"
	page_name = "showthread.php"
	forum_args = "?t="
	response = None
	try:
		post = urllib2.urlopen(core_url + page_name + forum_args + str(link_id))
		soup = BeautifulSoup(post, convertEntities=BeautifulSoup.HTML_ENTITIES)
		try:  # hating BeautifulSoup
			pattern = '((?:[a-z][a-z]+))' + '(_)' + '((?:[a-z][a-z]+))' + '(_)' + '(\\d+)'
			pattern = re.compile(pattern, re.DOTALL)
			response = soup.findAll("div", {"id": pattern})[0]
			response = response.findAll(text=True)
			response = ''.join(response)
			response = response.encode('ascii', 'ignore')
		except:
			return None
	except:
		print "Failing on:", core_url + page_name + forum_args + link_id
	return response


def go():
	labels = {612: 'ATM card', 671: 'Banking', 21: 'Business', 26: 'Church and Charity', 646: 'Commodities', 500: 'Compensation', 670: 'Delivery company', 648: 'Dying people', 644: 'Employment', 24: 'Government', 501: 'Loans', 20: 'Lottery', 643: 'Military', 660: 'Mystery Shopper', 23: 'Next of Kin', 659: 'Orphans', 25: 'Refugees', 29: 'Fake cheques', 16: 'Romance', 169: 'Romance', 669: 'Western Union and MoneyGram', 22: 'Widow'}
	misc = [502, 654, 480, 653, 9, 668, 645, 28, 656, 647]
	for i in misc:
		labels[i] = 'Misc'
	tl_count = len(labels)
	cl_count = 0
	for label in labels:
		cl_count += 1
		print "Forum count: %d/%d" % (cl_count, tl_count)
		all_links = crawlIndex(label)
		tl2_count = len(all_links)
		cl2_count = 0
		for link in all_links:
			cl2_count += 1
			print "Link count: %d/%d" % (cl2_count, tl2_count)
			response = crawlPost(link)
			if response:
				dirname = "_".join(labels[label].lower().split())
				try:
					os.makedirs('/tmp/419corpus/' + dirname)
				except OSError:
					pass
				fileh = open('/tmp/419corpus/' + dirname + '/' + str(link) + '.txt', 'w')
				fileh.write(response)
				fileh.flush()
				os.fsync(fileh)
				fileh.close()
	return
