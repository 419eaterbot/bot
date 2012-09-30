import os
import random
import time
from identity import getIdentityEmails
from email_classifier import hasPQ
from string import Template
from smtplib import SMTP_SSL
from email.MIMEText import MIMEText

def countScenarios(scenario_name):
	return len(filter(lambda x: '.txt' in x and '~' not in x, os.listdir('scenarios/' + scenario_name + '/')))

def getScenario(scenario_name):
	options = filter(lambda x: '.txt' in x and '~' not in x, os.listdir('scenarios/' + scenario_name + '/'))
	if options:
		return open('scenarios/' + scenario_name + '/' + random.choice(options)).read().strip()
	else:
		return ''

def answerPQ(text, identity_dict, email_class):
	paragraph = ""
	postcode_words = ['post code', 'postcode', 'zip']
	intro = getScenario('pq_intro') + os.linesep
	ending = os.linesep + getScenario('pq_ending') + os.linesep
	marriage = ""
	if email_class == 'romance':
		marriage = getScenario('marriage')
	if "....." in text or "_____" in text:
		body = getScenario('pq_generic')
		paragraph = os.linesep + ''.join([intro + os.linesep, body, os.linesep + ending]) + os.linesep
	else:
		name = getScenario('name')
		occupation = getScenario('occupation')
		age = getScenario('age')
		location = getScenario('location')
		postcode = ""
		for word in postcode_words:
			if text and word in text.lower():
				postcode = getScenario('postcode')
				break
		contact = getScenario('contact')
		paragraph = os.linesep + " ".join([intro, name, occupation, age, marriage, location, postcode, contact, ending]) + os.linesep
	paragraph = Template(paragraph).safe_substitute(identity_dict)
	id_answer, photo_answer = "", ""
	id_words = ['passport',' id ','id card','license', 'license']
	photo_words = ['photo', 'picture of']
	for word in id_words:
		if text and word in text.lower():
			paragraph += os.linesep + getScenario('photo_request') + os.linesep
			return paragraph
	for word in photo_words:
		if text and word in text.lower():
			paragraph += os.linesep + getScenario('photo_request') + os.linesep
			return paragraph
	return paragraph

def quoteText(email_dict):
	if email_dict['Body']:
		prefix = os.linesep + os.linesep + "On " + email_dict['Date'] + " <" + email_dict['Reply-To'] + "> wrote:" + os.linesep
		text = email_dict['Body']
		return prefix + "".join(["> " + x + os.linesep for x in text.splitlines()])
	else:
		return None

def composeGreeting(email_dict):
	if email_dict['First_name']:
		greeting = random.choice(['Dear', 'Hi', 'Hello'])
		return greeting + ' ' + email_dict['First_name'] + ',' + os.linesep
	else:
		return "Hello," + os.linesep

def composeSubject(email_dict):
	return "Re: " + email_dict['Subject']

def composeMessage(text, email_class, identity_dict, email_dict, state, solved_pq = False):
	message = (2 * os.linesep).join(['$Greeting', '$Body', '$Signoff', '$QuotedText'])
	message = message.replace(os. linesep + '$QuotedText', '$QuotedText')
	content = {'Greeting': composeGreeting(email_dict), 'Body': composeBody(text, email_class, identity_dict, email_dict, state, solved_pq), 'Signoff': composeSignoff(identity_dict), 'QuotedText': quoteText(email_dict)}
	return Template(message).safe_substitute(content)


def buildQuestionBody(email_class, maxscen = 4):
	question_count = random.choice(range(2, min(maxscen, countScenarios(email_class + '/' + 'question_body'))))
	current_count, question_body = 0, ''
	while True:
		random_scenario = getScenario(email_class + '/' + 'question_body')
		if random_scenario not in question_body:
			question_body += random_scenario + os.linesep
			current_count += 1
		if current_count == question_count:
			break
	return question_body

def getRuleAnswers(text, email_class):
	if text:
		text_l = text.lower()
	else:
		return None
	assocMap = {}
	if email_class == 'lottery':
		assocMap['form_approved'] = ['bank', 'payment', 'paying', 'approved']
		assocMap['payment_approved'] = ['affidavit', 'remit', 'wire transfer', 'attorney']
		assocMap['final_stage'] = ['service charge', 'charge', 'fee', 'wire transfer', 'sum of']
	elif email_class == 'mystery_shopper':
		assocMap['generic'] = ['a', 'b'] 
	elif email_class == 'orphans':
		assocMap['generic'] = ['a', 'b'] 
	else:
		return None
	for key in assocMap:
		for word in assocMap[key]:
			if word in text_l:
				return getScenario(email_class + '/' + key)
	return None

def hasTriggerWords(text, email_class):
	if text:
		text_l = text.lower()
	else:
		return False
	words = getScenario(email_class + '/' + 'trigger_words').splitlines()
	for word in words:
		if word in text_l:
			return True
	return False

def composeBody(text, email_class, identity_dict, email_dict, state, solved_pq = False):
	content = {}
	body = ['$Opening']
	if state == 0:
		content['Opening'] = getScenario(email_class + '/' + 'init')
		if not solved_pq:
			pq_status = hasPQ(text)
			if pq_status:
				if pq_status.values()[0]:
					body.append('$PQ_answer')
					content['PQ_answer'] = answerPQ(text, identity_dict, email_class)
		body.extend(['$Question_intro', '$Question_body'])
		content['Question_intro'] = getScenario(email_class + '/' + 'question_intro')
		content['Question_body'] = buildQuestionBody(email_class)
		body = (os.linesep).join(body)
	else:
		if not state % 2:
			content['Opening'] = getScenario('reopen')
		else:
			body = []
		if not solved_pq:
			pq_status = hasPQ(text)
			if pq_status:
				if pq_status.values()[0]:
					body.append('$PQ_answer')
					content['PQ_answer'] = answerPQ(text, identity_dict, email_class)
		if hasTriggerWords(text, email_class):
			body.append('$Rule_answers')
			content['Rule_answers'] = getRuleAnswers(text, email_class)
		if email_class != 'orphans':
			body.extend(random.choice([['$Story', '$Closing'], ['$Story']]))		
			content['Story'] = getScenario('story')
		else:
			body.append('$Closing')
		if '$Closing' in body:
			content['Closing'] = getScenario('closing')
		body = (2 * os.linesep).join(body)
	return Template(body).safe_substitute(content)


def composeSignoff(identity_dict):
	signoff = random.choice(['Kind Regards', 'Best Regards', 'Best Wishes', 'Warm Regards', 'Regards', 'Thanks', 'Thank you'])
	return signoff + ',' + os.linesep + random.choice([identity_dict['First_name'], " ".join([identity_dict['First_name'], identity_dict['Last_name']])])

def syncGuardian(mime_msg, identity_dict):
	del mime_msg['To']
	mime_msg['To'] = os.getenv('guardian_acc') # 'data.guardian@gmx.com'
	conn = SMTP_SSL(identity_dict['SMTP'])
	conn.set_debuglevel(False)
	conn.login(identity_dict['Username'], identity_dict['Password'])
	try:
		conn.sendmail(mime_msg['From'], mime_msg['To'], mime_msg.as_string())
	except:
		pass # No big deal
	finally:
		conn.close()
	return

def sendEmail(text, email_class, identity_dict, email_dict, state, solved_pq = False):
	retries, count = 3, 0
	while count < retries:
		try:
			message = composeMessage(text, email_class, identity_dict, email_dict, state, solved_pq)
			own_addr = identity_dict['Email']
			own_name = ' '.join([identity_dict['First_name'], identity_dict['Last_name']])
			destination_addr = email_dict['Reply-To']
			text_subtype = 'plain'
			mime_msg = MIMEText(message, text_subtype)
			mime_msg['Subject'] = composeSubject(email_dict)
			mime_msg['From'] = own_name + '<' + own_addr + '>'
			if destination_addr in getIdentityEmails():
				break
			mime_msg['To'] = destination_addr
			server_addr = identity_dict['SMTP']
			conn = SMTP_SSL(server_addr)
			conn.set_debuglevel(False)
			conn.login(identity_dict['Username'], identity_dict['Password'])
			try:
				conn.sendmail(own_addr, destination_addr, mime_msg.as_string())
			finally:
				print "Send email!"
				conn.close()
				syncGuardian(mime_msg, identity_dict)
		except Exception:
			count += 1
			continue
		pq_status, pq_result = hasPQ(text), None
		if pq_status:
			pq_result = hasPQ(text).values()[0]
		return {'Date': time.ctime(), 'Sender': own_addr, 'Receiver': destination_addr, 'Subject': composeSubject(email_dict), 'Body': message, 'First_name': identity_dict['First_name'], 'Last_name': identity_dict['Last_name'], 'Origin': 'SYSTEM', 'PQ': pq_result}
	return None
