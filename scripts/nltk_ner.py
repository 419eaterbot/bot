import sys
#sys.path.append('C:\Python26\Lib\site-packages')
import re, nltk, os, sys, email
def getNER(text):
	people, places = [], []
	text = nltk.sent_tokenize(text)
	for sent in text:
		chunks = nltk.ne_chunk(nltk.pos_tag(nltk.word_tokenize(sent)))
		for chunk in chunks:
			if hasattr(chunk, 'node'):
				if chunk.node == "PERSON":
					person = ' '.join(c[0] for c in chunk.leaves())
					people.append(person)
				if chunk.node == "GPE":
					place = ' '.join(c[0] for c in chunk.leaves())
					places.append(place)
	return (people, places)

def getEmails(text):
	mailsrch = re.compile(r'[\w\-][\w\-\.]+@[\w\-][\w\-\.]+[a-zA-Z]{1,4}')
	all_emails = []
	field_from = None
	field_replyto = None
	for line in text:
		res = mailsrch.findall(line)
		if res and res[0].split('@')[0].islower():			
			all_emails.append(res)
			if 'from' in line.lower() and len(line.split()) < 10:
				field_from = res
			if 'reply-to' in line.lower():
				field_replyto = res
	return (field_from, field_replyto, all_emails)

def main():
	files = []
	for filename in sys.argv[1:]:
		files.append(filename)
	for fil in files:
		field_from, field_replyto, all_emails = getEmails(open(fil, 'r').readlines())
		people, places = getNER(open(fil, 'r').read())
	print "Reply-To address: " + str(field_replyto)
	print "From address: " + str(field_from)
	print "All email addresses: " + str(all_emails)
	print "People positives: " + str(people)
	print "Places positives: " + str(places)

if __name__ == '__main__':
	main()
