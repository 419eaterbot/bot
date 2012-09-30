import os
import poplib
import time
from email import parser
import random
def formatMessage(message):
	msg_split = message.splitlines()
	to_delete = []
	headers = {'Date': None, 'From':None, 'Reply-To':None, 'Subject':None, 'To':None}
	count, cutoff = 0, len(msg_split) # better to skip a message than to expose user
	foundSubject = None
	for line in msg_split:
		if "forwarded message" in line.lower() and cutoff == len(msg_split):
			cutoff = count + 1
		if not foundSubject and "Subject:":
			foundSubject = count
		if "end forwarded" in line.lower() or "SC005336" in line:
			to_delete.append(count)
		for key in headers:
			if (key + ':') in line and not headers[key]:
				headers[key] = count
		count += 1
	if foundSubject:
		msg_split[foundSubject] = msg_split[foundSubject].replace('Fwd: ','')
		msg_split[foundSubject] = msg_split[foundSubject].replace('Fw:','')
	for key in headers:
		if headers[key]:
			msg_split[headers[key]] = msg_split[headers[key]].strip()
	count = 0
	for elem in to_delete:
		del msg_split[(elem - count)] # Headaches! ...
		count += 1
	result = os.linesep.join(msg_split[cutoff:])
	return result if [x for x in result if x.isalpha()] else None

def retrieveMessages(login_dict):
	output_dir = 'incoming'
	pop_conn = poplib.POP3_SSL(login_dict['POP3'])
	pop_conn.user(login_dict['Username'])
	pop_conn.pass_(login_dict['Password'])
	messages = [pop_conn.retr(i) for i in range(1, len(pop_conn.list()[1]) + 1)]
	[pop_conn.dele(i) for i in range(1, len(pop_conn.list()[1]) + 1)]
	pop_conn.quit()
	messages = ["\n".join(mssg[1]) for mssg in messages]
	messages = [parser.Parser().parsestr(mssg) for mssg in messages]
	for msg in messages:
		unique_id = str(random.choice(xrange(1,999999999)))
		output = msg.get_payload()
		output = formatMessage(output)
		if not output:
			continue
		tmpName, realName = output_dir + '/' + 'MBOX' + '-' + unique_id + '.tmp', output_dir + '/' + 'MBOX' + '-' + unique_id + '.ready'
		f = open(tmpName, 'w')
		f.write(output)
		f.flush()
		os.fsync(f)
		f.close()
		os.rename(tmpName, realName)
	return

if __name__ == "__main__":
	while True:
		try:
			print "Back to work!"
			login_dict = {}
			login_dict['POP3'] = os.getenv('mbox_pop') # e.g. 'pop.mail.yahoo.com'
			login_dict['Username'] = os.getenv('mbox_acc') # e.g. 'fraud.collector@yahoo.co.uk'
			login_dict['Password'] = os.getenv('mbox_pass') # e.g. 123456
			retrieveMessages(login_dict)
			idle = 4 * 60 * 60
			print "Waiting %d min." % (idle/60)
			time.sleep(idle)
		except Exception, e:
			print "Caught exception:", e
