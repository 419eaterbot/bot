import os
import poplib
import time
from email import parser
import random
from identity import createIdentities
def retrieveMessages(identity_dict):
	output_dir = 'incoming'
	pop_conn = poplib.POP3_SSL(identity_dict['POP3'])
	pop_conn.user(identity_dict['Username'])
	pop_conn.pass_(identity_dict['Password'])
	messages = [pop_conn.retr(i) for i in range(1, len(pop_conn.list()[1]) + 1)]
	print messages
	[pop_conn.dele(i) for i in range(1, len(pop_conn.list()[1]) + 1)]
	pop_conn.quit()
	messages = ["\n".join(mssg[1]) for mssg in messages]
	messages = [parser.Parser().parsestr(mssg) for mssg in messages]
	for msg in messages:
		replyto_addr = None
		output = ""
		unique_id = str(random.choice(xrange(1,999999999)))
		if msg['Reply-To']:
			replyto_addr = msg['Reply-To']
		else:
			replyto_addr = msg['From']
		output += "From: " + replyto_addr + os.linesep
		output += "To: " + msg['To'] + os.linesep
		output += "Date: " +  msg['Date'] + os.linesep
		output += "Subject: " + msg['Subject'] + os.linesep
		output += os.linesep
		try:
			output += msg.get_payload()
		except:
			payload = msg.get_payload()
			found = False
			if payload:
				for part in payload:
					print "before if"
					if 'Content-type' in part and "text/plain" in part['Content-type']:
						print "After if"
						output += part.get_payload()
						found = True
						break
				if not found:
					for part in payload:
						if 'Content-type' in part and "text/html" in part['Content-type']:
							output += part.get_payload()
							break
		print output
		tmpName, realName = output_dir + '/' + 'IDENTITY' + '-' + unique_id + '.tmp', output_dir + '/' + 'IDENTITY' + '-' + unique_id + '.ready'
		f = open(tmpName, 'w')
		f.write(output)
		f.flush()
		os.fsync(f)
		f.close()
		os.rename(tmpName, realName)
	return

if __name__ == "__main__":
	while True:
		identities = createIdentities()
		for identity in identities:
			try:
				print "Checking", identities[identity]['Username']
				retrieveMessages(identities[identity])
			except Exception, e:
				print "Caught exception:", e
			finally:
				time.sleep(2.5)
		idle = random.choice([x for x in range(10,21) if not x%5]) * 60
		print "Waiting %d min." % (idle/60)
		time.sleep(idle)
