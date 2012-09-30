import random
def getRandomIdentity():
	identities = createIdentities()
	key = random.choice(list(identities.keys()))
	return (key, identities[key])

def getIdentityEmails():
	identities = createIdentities()
	return [identities[identity]['Email'] for identity in identities]

def getIdentityByName(first_name, last_name):
	if first_name and last_name:
		allIDs = createIdentities()
		for identity in allIDs:
			if (allIDs[identity]['First_name'].lower() == first_name.lower()) and (allIDs[identity]['Last_name'].lower() == last_name.lower()):
				return (identity, allIDs[identity])
	return None

def getIdentityByEmail(email_addr):
	allIDs = createIdentities()
	for identity in allIDs:
		if allIDs[identity]['Email'] == email_addr:
			return (identity, allIDs[identity])
 	return None
 
def getIdentityByID(ID):
	allIDs = createIdentities()
	try:
		return allIDs[ID]
	except KeyError:
		return None

def createIdentities(): # TODO: move identities KB to an encrypted DB.
	identities = {}
	identities[0] = {'Gender': 'male', 'Age': '47', 'Marriage': 'Single', 'First_name': 'Ethan', 'Last_name': 'Stokes', 'Occupation': 'an accountant', 'Address': '21 Quay Street', 'City':'Manchester', 'Country':'UK','Postcode': 'M3 4AE', 'Telephone':'07425902430', 'Email': 'ethanstokes51@yahoo.co.uk', 'POP3': 'pop.mail.yahoo.com', 'SMTP': 'smtp.mail.yahoo.com', 'Username': 'ethanstokes51@yahoo.co.uk', 'Password': ''}
	return identities
