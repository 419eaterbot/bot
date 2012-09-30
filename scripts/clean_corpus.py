import os
import glob
from clean_email import *

def prepareFileContent(text):
	if extractInfo(text):
		return text
	return None

def cleanCorpus():
	dirs = ['atm_card', 'employment', 'next_of_kin', 'banking', 'fake_cheques', 'orphans', 'business', 'government', 'refugees', 'church_and_charity', 'loans', 'romance', 'commodities', 'lottery', 'western_union_and_moneygram', 'compensation', 'military', 'widow', 'delivery_company', 'misc', 'dying_people', 'mystery_shopper']
	orig_path = '/tmp/corpus_dirty/'
	clean_path = '/tmp/corpus_clean/'
	count = 0
	for d in dirs:
		full_orig_path = orig_path + d + '/'
		for filename in glob.glob(os.path.join(full_orig_path, '*.txt')):
			count += 1
			print "Count: ", count
			rtext = open(filename, 'r').read()
			result = prepareFileContent(rtext)
			if result:
				try:
					os.makedirs(clean_path + d + '/')
				except OSError:
					pass
				f_clean = open(clean_path + d + '/' + str(filename).split('/')[-1], 'w')
				f_clean.write(rtext)
				f_clean.flush()
				os.fsync(f_clean)
				f_clean.close()