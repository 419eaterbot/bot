## Prepare data for the classifier
import os
import glob
import nltk
from clean_email import removeHeaders

def removeAllHeaders():
	dirs = ['atm_card', 'employment', 'next_of_kin', 'banking', 'fake_cheques', 'orphans', 'business', 'government', 'refugees', 'church_and_charity', 'loans', 'romance', 'commodities', 'lottery', 'western_union_and_moneygram', 'compensation', 'military', 'widow', 'delivery_company', 'misc', 'dying_people', 'mystery_shopper']
	for d in dirs:
		path = '/home/fusion/dev/419/' + d + '/'
		for filename in glob.glob(os.path.join(path, '*.txt')):
			f = open(filename, 'r')
			content = removeHeaders(f.read())
			f.close()
			f = open(filename, 'w')
			f.write(content)
			f.close()

def splitData():
		dirs = ['atm_card', 'employment', 'next_of_kin', 'banking', 'fake_cheques', 'orphans', 'business', 'government', 'refugees', 'church_and_charity', 'loans', 'romance', 'commodities', 'lottery', 'western_union_and_moneygram', 'compensation', 'military', 'widow', 'delivery_company', 'misc', 'dying_people', 'mystery_shopper']
		allTrainFiles = []
		allTestFiles = []
		for d in dirs:
			path = '/home/fusion/dev/419_train/' + d + '/'
			full_count =  len([name for name in os.listdir(path)])
			curr_count = 0 
			trainFilenames = []
			for filename in glob.glob(os.path.join(path, '*.txt')):
				curr_count += 1
				if curr_count <= 0.8 * float(full_count):
					trainFilenames.append(filename.split('/')[-1])
					allTrainFiles.append(filename.split('/')[-1])
				else:
					os.remove(filename)
			path = '/home/fusion/dev/419_test/' + d + '/'
			for filename in glob.glob(os.path.join(path, '*.txt')):
				if filename.split('/')[-1] in trainFilenames:
					os.remove(filename)
				else:
					allTestFiles.append(filename.split('/')[-1])
		return (allTrainFiles, allTestFiles)

def buildPropertyFile():
			dirs = ['atm_card', 'employment', 'next_of_kin', 'banking', 'fake_cheques', 'orphans', 'business', 'government', 'refugees', 'church_and_charity', 'loans', 'romance', 'commodities', 'lottery', 'western_union_and_moneygram', 'compensation', 'military', 'widow', 'delivery_company', 'misc', 'dying_people', 'mystery_shopper']
			total = ""
			for d in dirs:
				path = '/home/fusion/dev/419_train/' + d + '/'
				for filename in glob.glob(os.path.join(path, '*.txt')):
					content = open(filename).readlines()
					output = ""
					for line in content:
						output += line.strip() + ' '
					for l in output:
						if l.isalpha():
							total += d + '\t' + output + os.linesep
							break
			f = open('train.set', 'w')
			f.write(total)
			total = ""
			for d in dirs:
				path = '/home/fusion/dev/419_test/' + d + '/'
				for filename in glob.glob(os.path.join(path, '*.txt')):
					content = open(filename).readlines()
					output = ""	
					for line in content:
						output += line.strip() + ' '
					for l in output:
						if l.isalpha():
							total += d + '\t' + output + os.linesep
							break
			f = open('test.set', 'w')
			f.write(total)


def makeBinaryClassif():
	path_info = '/home/fusion/dev/419_train/info/'
	path_noinfo = '/home/fusion/dev/419_train/no_info/'
	path = '/home/fusion/dev/419_train/'
	count = 0
	for filename in glob.glob(os.path.join(path, '*.txt')):
		count += 1
		print "Count", count
		content = open(filename).read()
		if "name" in content.lower():
			asking = True
			while asking:
				print content
				resp = raw_input('Does this contain questions?')
				if resp.lower() == 'y':
					asking = False
					f = open(path_info + filename.split('/')[-1], 'w')
					f.write(content)
					f.flush()
					f.close()
				elif resp.lower() == 'n':	
					asking = False
					f = open(path_noinfo + filename.split('/')[-1], 'w')
					f.write(content)
					f.flush()
					f.close()
				elif resp.lower() == 'q':
					asking = False
					print "Quitting & saving"
		else:
			f = open(path_noinfo + filename.split('/')[-1], 'w')
			f.write(content)
			f.flush()
			f.close()




def makeTop():
			dirs = ['atm_card', 'employment', 'next_of_kin', 'banking', 'fake_cheques', 'orphans', 'business', 'government', 'refugees', 'church_and_charity', 'loans', 'romance', 'commodities', 'lottery', 'western_union_and_moneygram', 'compensation', 'military', 'widow', 'delivery_company', 'misc', 'dying_people', 'mystery_shopper']	
			stopwords = nltk.corpus.stopwords.words('english')
			dicts = []
			for d in dirs:
				path = '/home/fusion/dev/419/' + d + '/'
				allwords = {}
				for filename in glob.glob(os.path.join(path, '*.txt')):
					content = open(filename).read().split()
					for word in content:
						w = word.strip().lower()
						if w in allwords:
							allwords[w] += 1
						else:
							if w not in stopwords:
								allwords[w] = 1
				dicts.append(allwords)
			return dicts