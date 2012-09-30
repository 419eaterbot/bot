import os
import glob
from clean_email import cleanHeader_heuristic


def buildHeaderDB():
	path = os.environ['HOME'] + '/dev/proj/data/test/'
	valid = []
	invalid = []
	try:
		dict_read = open(os.environ['HOME'] + '/dev/proj/data/headers.txt', 'r')
		for line in dict_read:
			if line not in valid:
				valid.append(line)
	except IOError:
		pass
	dictionary = open(os.environ['HOME'] + '/dev/proj/data/headers.txt', 'a')
	count = 0
	for filename in glob.glob(os.path.join(path, '*.txt')):
		count += 1
		print "count:", count
		print "current file is:", filename
		text = open(filename, 'r').read()
		headers = cleanHeader_heuristic(text)
		for candidate in headers:
			cand = candidate.split(':')[0] + ':'
			if cand not in valid and cand not in invalid:
				asking = True
				while asking:
					print cand
					resp = raw_input('Is this a header?')
					if resp.lower() == 'y':
						asking = False
						valid.append(cand)
						dictionary.write(cand + os.linesep)
						dictionary.flush()
						os.fsync(dictionary)
					elif resp.lower() == 'n':
						asking = False
						invalid.append(cand)
					elif resp.lower() == 'q':
						asking = False
						print "Quitting & saving"
	print "Done."
	return
