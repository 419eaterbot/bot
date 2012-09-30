import os
import glob
from clean_email import *


def prepareFileContent(text):
	if extractInfo(text):
		return (removeHeaders(text), text)
	return None


def buildFileDir():
	orig_path = os.environ['HOME'] + '/dev/proj/data/test/'
	path1 = os.environ['HOME'] + '/dev/proj/data/no-headers/'
	path2 = os.environ['HOME'] + '/dev/proj/data/with-headers/'
	count = 0
	for filename in glob.glob(os.path.join(orig_path, '*.txt')):
		count += 1
		print "Count:", count
		rtext = open(filename, 'r').read()
		result = prepareFileContent(rtext)
		if result:
			w_no_headers = open(path1 + str(filename).split('/')[-1], 'w')
			w_with_headers = open(path2 + str(filename).split('/')[-1], 'w')
			text_no_headers, text_with_headers = result[0], result[1]
			w_no_headers.write(text_no_headers)
			w_with_headers.write(text_with_headers)
			w_no_headers.flush()
			w_with_headers.flush()
			os.fsync(w_no_headers)
			os.fsync(w_with_headers)
			w_no_headers.close()
			w_with_headers.close()
	print "Done."
	return
