import pdb
import pickle
def doIt():
	out = {}
	with open("stopwords.txt") as f:
		for line in f:
			out[str(line).strip()] = True
	with open("stopwords.p", 'wb') as f:
   		pickle.dump(out, f)

doIt()