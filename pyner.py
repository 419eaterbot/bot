# Simple Python wrapper for Stanford NER
import os
import re

class Pyner(object):
	def __init__(self):
		self.cmd = 'java -mx700m -cp classifiers/crf.jar edu.stanford.nlp.ie.crf.CRFClassifier -loadClassifier models/all.3class.distsim.crf.ser.gz -textFile '

	def getNames(self, filename):
		self.currentcmd = self.cmd + filename
		output = os.popen(self.currentcmd, 'r')
		out = ""
		for line in output:
			out += line.strip()
		output.close()
		out = out.split()
		names, count, current_name = [], 0, ""
		title = re.compile(r"^\s*(mr|mrs|dr|ms|miss)[\.\s]+", flags=re.IGNORECASE)
		for element in out:
			count += 1
			if element.count('/') == 1:
				word, tag = element.split('/')
				if tag == "PERSON" and not current_name:
					if title.match(word + "."):
						continue
					else:
						current_name = word
				elif tag == "PERSON" and current_name:
					current_name += " " + word
					if len(out) == count:
						names.append(current_name)
				elif tag != "PERSON" and current_name:
					names.append(current_name)
					current_name = ""
		return names
