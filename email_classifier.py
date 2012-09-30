from pycla import Pycla
import hashlib
def overrides(text):  # Overrides. If email contains any of these phrases, we don't need to run the classifier.
	if not text:
		return None
	text = text.lower()
	if "next of kin" in text:
		return "next_of_kin"
	if "western union" in text or "moneygram" in text:
		return "western_union_and_moneygram"
	if "lottery" in text and "winner" in text:
		return "lottery"
	return None

def fallback(text): # Fallbacks. If the classifier can't tell with confidence, let's just make a reasonable guess.
	if not text:
		return None
	text = text.lower()
	if "job" in text:
		return "employment"
	if ("father" in text or "mother" in text) and "died":
		return "orphans"
	if "government" in text:
		return "government"
	if "country" in text and "father" in text:
		return "refugees"
	if "gold" in text or "oil" in text or "crude" in text:
		return "commodities"
	if "late husband" in text or ("husband" in text and "death" in text):
		return "widow"
	if "health" in text or "cancer" in text:
		return "dying_people"
	if "mystery" in text and "shop" in text:
		return "mystery_shopper"
	if "atm" in text and ("card" in text or "machine" in text):
		return "atm_card"
	if "foundation" in text:
		return "church_and_charity"
	if "loan" in text:
		return "loans"
	return None

def classify(text):
	if not text:
		return None
	batch, hashes = {}, {}
	if type(text) is str:
		text = [text]
	text_prob = text
	# Compute hashes / keys
	# Process the overrides first
	for t in text:
		p_hash = hashlib.sha224(t).hexdigest()
		hashes[p_hash] = t
		over = overrides(t)
		if over:
			batch[p_hash] = over
			text_prob.remove(t)
	# Call the Maxent classifier on the remaining items
	if text_prob:
		maxent = Pycla('419classifier.ser.gz')
		result = maxent.classify(text_prob)
		failed = []
		for elem in result:
			if result[elem][1] > 0.4:
				batch[elem] = result[elem][0]
			else:
				failed.append(hashes[elem])
		# Attempt fallback on low probability classifications
		# Return None for unsuccessful.
		for t in failed:
			p_hash = hashlib.sha224(t).hexdigest()
			batch[p_hash] = fallback(t)
	return batch

def hasPQ(text):
	if not text:
		return None
	batch = {}
	if type(text) is str:
		text = [text]
	maxent = Pycla('PQclassifier.ser.gz')
	result = maxent.classify(text)
	for elem in result:
		if result[elem][0] == 'info':
			batch[elem] = True
		else:
			batch[elem] = False
	return batch
	
