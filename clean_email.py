'''
Information Extraction
The _safe methods are in cases where we need not worry about dirty input.
'''
import os
import re
import time
from BeautifulSoup import BeautifulSoup
from pyner import Pyner


# STEP -1 - Remove HTML
def removeHTML(text):
	msg_split = text.splitlines()
	for i in range(0, len(msg_split)):
		if extractEmails(msg_split[i]):
			if '>' in msg_split[i] and '<' in msg_split[i]:
				msg_split[i] = msg_split[i].replace('<','< ')
	text = os.linesep.join(msg_split)
	return ''.join(BeautifulSoup(text, convertEntities='html').findAll(text=True)).encode('ascii', 'ignore')

# STEP 0 - Attempt to remove quotes. This fails, should the message not be prefixed properly: >
def removeQuotes(text):
	text_splitlines = text.splitlines()
	count, cutoff = 0, len(text_splitlines)
	for line in text_splitlines:
		if '>' in line and line.index('>') < 2:
			cutoff = count - 1
			break
		count += 1
	return os.linesep.join(text_splitlines[:cutoff])

def removeQuotes_safe(text):
	text_splitlines = text.splitlines()
	count, cutoff, headerCount = 0, len(text_splitlines), {'Date:': 0, 'From:': 0, 'To:': 0, 'Subject:' : 0}
	for line in text_splitlines:
		for header in headerCount:
			if header in line and line.index(header) < 5:
				headerCount[header] += 1
				if headerCount.values().count(2) == 2: # at least two matches
					return os.linesep.join(text_splitlines[:cutoff])
				else:
					cutoff = count - 1
		count += 1
	count, count = len(text_splitlines), 0
	for line in text_splitlines:
		if '>' in line and line.index('>') < 2:
			cutoff = count - 1
			break
		count += 1
	return os.linesep.join(text_splitlines[:cutoff])

# STEP 1 - Clean up useless headers (Takes the message as a string)
def cleanHeaders(text, full=False):
	headers_file, headers_write, headers = open('data/headers.txt', 'r'), open('data/headers.txt','w'), []
	regexp = '(X)' + '(-)' + '((?:[a-z][a-z0-9_]*))' + '(-)' + '((?:[a-z][a-z0-9_]*))' + '(:)'
	regexp = re.compile(regexp, re.IGNORECASE | re.DOTALL)
	msg_lines = text.splitlines()
	maxh, output = 0, ""
	for h in headers_file:
		headers.append(h.strip())
	for i in range(0, len(msg_lines)):
		if regexp.findall(msg_lines[i]):
#			headers_write(msg_lines[i])
			maxh = i
		for h in headers:
			if h in msg_lines[i]:
				maxh = i
				break
	if full:
		for i in range(maxh + 1, len(msg_lines)):
			output += msg_lines[i] + os.linesep
	else:
		exceptions = ['Reply-To:', 'Reply-to:', ' Reply-To:', 'In-Reply-To:', 'Subject:', 'To:', ' To:', 'From:']
		for i in range(0, len(msg_lines)):
			if i <= maxh:
				for h in exceptions:
					if h in msg_lines[i]:
						output += msg_lines[i] + os.linesep
						break
			else:
				output += msg_lines[i] + os.linesep
	return output


def cleanHeader_heuristic(text, full=False):  # this is a heuristic method, unused except for creating training data
	msg_lines = text.splitlines()
	headers = []
	for line in msg_lines:
		foundAlpha = False
		for i in range(0, len(line)):
			char = line[i]
			if char.isalpha() and not foundAlpha:
				foundAlpha = True
				if char.isupper():
					count = 0
					while True:
						count += 1
						try:
							if line[i + count].isalpha() or line[i + count] == '-':
								pass
							elif line[i + count] == ':':
								if line[i + count + 1] == " ":
									headers.append(line)
									break
							else:
								break
						except:
							break
	return headers


# STEP 2 - Extract useful headers. (Takes the message as a string)
def extractHeaders(text):
	mailsrch = re.compile(r'[\w\-][\w\-\.]+@[\w\-][\w\-\.]+[a-zA-Z]{1,4}')
	msg_lines = text.splitlines()
	headers = {'Reply-To': None, 'From': None, 'To': None, 'Subject': None}
	for line in msg_lines:
		for header in headers:
			if header in line and headers[header] == None:
				if line and line.strip().index(header) < 2:
					if header == 'Subject':
						headers[header] = line.replace('Subject:', '').strip()
					else:
						regexp = mailsrch.findall(line)
						if regexp:
							headers[header] = regexp[0].strip()
	return headers

def extractHeaders_safe(text):
	mailsrch = re.compile(r'[\w\-][\w\-\.]+@[\w\-][\w\-\.]+[a-zA-Z]{1,4}')
	headers = {'Reply-To': None, 'From': None, 'To': None, 'Subject': None, 'Date': None}
	if text:
		msg_lines = text.strip().splitlines()
	else:
		return headers
	for line in msg_lines:
		for header in headers:
			header_colon = header + ':'
			if header_colon in line:
				if (header == 'Subject' or header == 'Date'):
					if not headers[header]:
						headers[header] = line.replace(header_colon, '').strip()
					else:
						break
				else:
					regexp = mailsrch.findall(line)
					if regexp:
						if not headers[header]:
							headers[header] = regexp[0].strip()
						else:
							break
	return headers


# STEP 3 - Remove all headers. (Takes the message as a string)
def removeHeaders(text):
	return cleanHeaders(text, full=True)

def removeHeaders_safe(text):
	if not text:
		return text
	msg_lines, cutoff = text.strip().splitlines(), 0
	for line in msg_lines:
		if line:
			cutoff += 1
		else:
			break
	return os.linesep.join(msg_lines[cutoff:]).strip()


# STEP 4 - Named Entity Recognition (Takes the message as a string)
def extractNames(text):
	f = open('ner.tmp', 'w')
	f.write(text)
	f.close()
	ner = Pyner()
	result = ner.getNames('ner.tmp')
	os.remove('ner.tmp')
	return result

def extractNames_safe(text, first_name, last_name):
	names = extractNames(text)
	return filter(lambda x: first_name not in x and last_name not in x, names)

# STEP 5 - Get all email addresses from the body of the text
def extractEmails(text):
	mailsrch = re.compile(r'[\w\-][\w\-\.]+@[\w\-][\w\-\.]+[a-zA-Z]{1,4}') # extract all email addrs
	return list(set(mailsrch.findall(text)))

def extractEmails_safe(text, identity_email):
	result = extractEmails(text)
	return filter(lambda x: x != identity_email, result)

# STEP 6 - Relate email addresses from body to people
def getBigrams(string):
	s = string.lower()
	return [s[i:i + 2] for i in xrange(len(s) - 1)]


def stringSim(str1, str2):
	pairs1 = getBigrams(str1)
	pairs2 = getBigrams(str2)
	union = len(pairs1) + len(pairs2)
	hit_count = 0
	for x in pairs1:
		for y in pairs2:
			if x == y:
				hit_count += 1
	return (2.0 * hit_count) / union


def rankSim(email_addr, name):
	name_var = [''.join(name.split())]
	name_var.extend(name.split())
	name_var = filter(lambda x: len(x) > 1, name_var)
	email_var = email_addr.split('@')[0]
	email_var = filter(lambda x: x.isalpha(), email_var)
	return max([stringSim(n, email_var) for n in name_var])


def computeRanking(names, email_addrs):
	ranking = {}
	email_addrs = [x.lower() for x in email_addrs]
	for email_addr in email_addrs:
		for name in names:
			score = rankSim(email_addr, name)
			if email_addr in ranking:
				if score > ranking[email_addr][1]:
					ranking[email_addr] = (name, score)
			else:
				ranking[email_addr] = (name, score)
	return ranking


def proximitySearch(name, text):
	text = text.splitlines()
	text = filter(None, text)
	mailsrch = re.compile(r'[\w\-][\w\-\.]+@[\w\-][\w\-\.]+[a-zA-Z]{1,4}')
	for i in range(0, len(text)):
		if name in text[i]:
			if mailsrch.findall(text[i]):
				return (mailsrch.findall(text[i])[0].lower(), 0)
			if i + 1 < len(text):
				if mailsrch.findall(text[i + 1]):
					return (mailsrch.findall(text[i + 1])[0].lower(), 1)
			if i > 0:
				if mailsrch.findall(text[i - 1]):
					return (mailsrch.findall(text[i - 1])[0].lower(), 1)
			if i + 2 < len(text):
				if mailsrch.findall(text[i + 2]):
					return (mailsrch.findall(text[i + 2])[0].lower(), 2)
			if i > 1:
				if mailsrch.findall(text[i - 2]):
					return (mailsrch.findall(text[i - 2])[0].lower(), 2)
	return None


def relateEntities(names, emails, text):
	emails = [x.lower() for x in emails]
	relations = {}
	if names and emails:
		rankings = computeRanking(names, emails)
	else:
		return relations
	for entity in rankings:
		if rankings[entity][1] > 0.4:
			relations[entity] = rankings[entity][0]
	if relations.values():
		rels_values = [x[0].lower() for x in relations.values()]
	else:
		rels_values = []
	rels_keys = [x.lower() for x in relations.keys()]
	names = filter(lambda x: x.lower() not in rels_values, names)
	emails = filter(lambda x: x.lower() not in rels_keys, emails)
	proximity_scores = {}
	if emails:
		for name in names:
			email_score = proximitySearch(name, text)
			if email_score and email_score[0].lower() not in rels_keys:
				email_addr, score = email_score[0], email_score[1]
				if email_addr in proximity_scores:
					if score < proximity_scores[email_addr][1]:  # looking for minimal score
						proximity_scores[email_addr] = (name, score)
				else:
					proximity_scores[email_addr] = (name, score)
	for email_addr in proximity_scores:
		relations[email_addr] = proximity_scores[email_addr][0]
	return relations


# STEP 7 Something to piece the puzzle all together....
def extractInfo(text, safe=False, identity_dict=None):
	if not safe:
		messages = []
		date = time.ctime()
		text_with_headers = cleanHeaders(text)
		headers = extractHeaders(text_with_headers)
		text = removeHeaders(text_with_headers)
		names = extractNames(text)
		emails = extractEmails(text)
		if not emails:
			if headers['Reply-To']:
				email_addr = headers['Reply-To']
			elif headers['From']:
				email_addr = headers['From']
			else:
				email_addr = None
			if email_addr:
				msg, msg['Date'], msg['Reply-To'], msg['To'], msg['Subject'], msg['Body'] = {}, date, email_addr, headers['To'], headers['Subject'], text
				if names:
					msg['First_name'], msg['Last_name'] = " ".join(names[-1].split()[:-1]), names[-1].split()[-1]
				else:
					msg['First_name'], msg['Last_name'] = None, None
				messages.append(msg)
			else:
				return []
			return messages
		unassoc_names = names
		relations = relateEntities(names, emails, text)
		for email in relations:
			emails = filter(lambda x: x != email, emails)
			unassoc_names = filter(lambda x: x != relations[email], unassoc_names)
			msg, msg['Date'], msg['Reply-To'], msg['To'], msg['Subject'], msg['Body'], msg['First_name'], msg['Last_name'] = {}, date, email, headers['To'], headers['Subject'], text, " ".join(relations[email].split()[:-1]), relations[email].split()[-1]
			print '1:', msg['First_name']
			messages.append(msg)
		email_addr = None
		for email in emails:
			if email == headers['Reply-To']:
				email_addr = email
			if email == headers['From'] and not email_addr:
				email_addr = email
		if email_addr:
			if unassoc_names and names:
				if unassoc_names[-1] == names[-1]:
					msg, msg['Date'], msg['Reply-To'], msg['To'], msg['Subject'], msg['Body'], msg['First_name'], msg['Last_name'] = {}, date, email, headers['To'], headers['Subject'], text, " ".join(names[-1].split()[:-1]), names[-1].split()[-1]
					messages.append(msg)
				else:
					msg['Date'], msg['Reply-To'], msg['To'], msg['Subject'], msg['Body'], msg['First_name'], msg['Last_name'] = date, email, headers['To'], headers['Subject'], text, None, None
					messages.append(msg)
		return messages
	else:
		messages, identity_email, first_name, last_name = [], identity_dict['Email'], identity_dict['First_name'], identity_dict['Last_name']
		text = removeQuotes(removeHTML(text))
		headers = extractHeaders_safe(text)
		body = removeHeaders_safe(text)
		names = extractNames_safe(body, first_name, last_name)
		emails = extractEmails_safe(body, identity_email)
		relations = relateEntities(names, emails, body)
		if headers['Date']:
			date = headers['Date']
		else:
			date = time.ctime()
		for rel in relations:
			msg = {}
			msg['Date'] = date
			msg['Reply-To'] = rel
			msg['To'] = identity_email
			msg['Subject'] = headers['Subject']
			msg['Body'] = body
			msg['First_name'] = " ".join(relations[rel].split()[:-1])
			msg['Last_name'] = relations[rel].split()[-1]
			messages.append(msg)
		hasOriginal = False
		for msg in messages:
			if headers['From'] == msg['Reply-To'] or headers['Reply-To'] == msg['Reply-To']:
				hasOriginal = True
		if not hasOriginal:
			msg = {}
			msg['Date'] = date
			if headers['Reply-To']:
				msg['Reply-To']
			elif headers['From']:
				msg['Reply-To'] = headers['From']
			else:
				return messages
			msg['To'] = identity_email
			msg['Subject'] = headers['Subject']
			msg['Body'] = body
			msg['First_name'], msg['Last_name'] = None, None
			messages.append(msg)
		return messages


def getEmails(text):
	emails = []
	text = removeHTML(text)
	clean_text = cleanHeaders(text)
	headers = extractHeaders(clean_text)
	if headers['From']:
		emails.append(headers['From'])
	if headers['Reply-To']:
		emails.append(headers['Reply-To'])
	clean_text = removeHeaders(clean_text)
	emails.extend(extractEmails(clean_text))
	headers = extractHeaders_safe(text)
	if headers['From']:
		emails.append(headers['From'])
	if headers['Reply-To']:
		emails.append(headers['Reply-To'])
	clean_text = removeHeaders_safe(text)
	emails.extend(extractEmails(clean_text))
	return list(set([x.lower() for x in emails]))

def prettyPrint(text):
	messages = extractInfo(text)
	for msg in messages:
		print os.linesep
		print "Date:", msg['Date']
		print "Reply-To:", msg['Reply-To']
		print "To:", msg['To']
		print "Subject:", msg['Subject']
		try:
			print "Name:", " ".join([msg['First_name'], msg['Last_name']])
		except:
			print "Name: no named entities found"
		print "Body:"
		print msg['Body']
	return
