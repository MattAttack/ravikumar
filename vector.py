import pickle
import math

class vector():
	def __init__(self,wordsFromEmail,wordsWeights):
		self.data = {}
		self.smoothing = 0.9
		self.initializeVector(wordsFromEmail,wordsWeights)

	def initializeVector(self,wordsFromEmail,wordsWeights):
		for word in wordsFromEmail:
			#multiply the number of times this word appears in an email by the inverse of its popularity
			self.data[word] = wordsFromEmail[word]

	def similarityTest(self,vectorB,wordsWeights):
		s = self.smoothing
		total = wordsWeights['totalNumbers']*1.0
		#Formula for cosine similarity is A * B 
		#						  		 -------
		#								 |A|*|B|
		num = 0.0
		dA = 1.0
		dB = 1.0

		#TODO: change type from float to cdecimal to prevent overflow errors
		for word in wordsWeights.keys():
			multiplier = (total/wordsWeights[word]) #calculate the weight of that word in real time, this weight is the inverse of popularity

			num = num + (multiplier*self.data.get(word,s))*(multiplier*vectorB.data.get(word,s)) #multiply the number of occurences of each word by the word's respective weight
			dA = dA * self.data.get(word,s)*multiplier
			dB = dB * vectorB.data.get(word,s)*multiplier

		den = math.sqrt(dA)*math.sqrt(dB)
		fraction = num/den
		return fraction

	def appendVector(self, vectorB):
		bData = vectorB.data
		for word in bData.keys():
			self.data[word] = self.data.get(word,0) + bData[word]



