import random
from smtplib import SMTP_SSL
from email.MIMEText import MIMEText
from responder import composeSignoff
from identity import getIdentityEmails, getIdentityByID
from main import init
import time
def sendRequest(conv_store):
	for key in conv_store:
		message = random.choice(['Hello', 'Hi'])
		message += '\n'
		message += '\n'
		message += 'I am interested to find out more about this. Please send me the full details.'
		message += '\n'
		message += 'Thanks,'
		message += '\n'
		message += 'Peter'
		own_addr = 'petersmith5566@yahoo.co.uk'
		own_name = 'Peter Smith'
		bucket = conv_store[key]['Bucket']
		mime_msg = MIMEText(message, 'plain')
		mime_msg['From'] = own_name + ' <' + own_addr + '>'
		if not bucket:
			continue
		else:
			destination_addr = bucket[0]
		for email_addr in bucket:
			if email_addr not in getIdentityEmails():
				mime_msg['To'] = email_addr
		if conv_store[key]['Messages'][0]['Subject']:
			mime_msg['Subject'] = "Re: " + conv_store[key]['Messages'][0]['Subject']
		else:
			mime_msg['Subject'] = "Re: "
		server_addr = 'smtp.mail.yahoo.com'
		conn = SMTP_SSL(server_addr)
		conn.set_debuglevel(True)
		conn.login(own_addr, 'test123')
		try:
			print "Preview:\n"
			print mime_msg.as_string()
			conn.sendmail(own_addr, destination_addr, mime_msg.as_string())
		finally:
			print "Send email!"
			conn.close()
			time.sleep(10)	

if __name__ == "__main__":
	a, b = init()
	sendRequest(b)
