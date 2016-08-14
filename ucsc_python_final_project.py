# Note - this code must run in Python 2.x and you must download
# http://www.pythonlearn.com/code/BeautifulSoup.py
# Into the same folder as this program

import matplotlib.pyplot as plt
import urllib2
import re
from BeautifulSoup import *
from sklearn.linear_model import LinearRegression
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import PolynomialFeatures
import numpy

class StockScraper():
	#constructor
	def __init__(self, url=None):
		self.url = url
		if self.url is not None:
			self.get_url()
		
	def get_url(self):
		self.valid_url = False
		#keep asking for a URL until a valid one is entered
		while not self.valid_url:
			self.url = raw_input("Please enter the URL of the Yahoo page of the stock you want to check: \n")
			try:
				#open the page
				self.html = urllib2.urlopen(self.url).read()
			except:
				print 'You have provided an invalid URL.\n'
			else:
				#once a valid URL is given, parse the page
				self.soup = BeautifulSoup(self.html)
				self.valid_url = True

	def scrape(self):
		#retrieve all of the td tags and get the stock price table
		self.tags = self.soup('td')
		self.stock_data = [tag.string for tag in self.tags if tag.get('class', None) == "yfnc_tabledata1"]
		self.stock_close_prices = [float(self.stock_data[i+4]) for i in range(0, len(self.stock_data) - 1, 7)]
		self.stock_days = range(len(self.stock_close_prices))
		self.first_day = self.stock_data[-8]

		print 'Stock data since %s has been retrieved.\nFitting a polynomial regression model...' %(self.first_day)
		
		#format the data
		self.stock_days = numpy.reshape(self.stock_days, (len(self.stock_days), 1))
		self.stock_close_prices = numpy.reshape(self.stock_close_prices, (len(self.stock_close_prices), 1))

		#the highest degree of the polynomials to be used in the polynomial regression
		self.degree = 5

		#create a pipeline to create polynomials and pipeline them into the classifier
		self.model = Pipeline([('poly', PolynomialFeatures(degree=self.degree)), ('linear', LinearRegression(fit_intercept=False))])

		#train the model
		self.model = self.model.fit(self.stock_days, self.stock_close_prices)

		print 'Polynomial regression model has been fitted.\n'


	def plot(self):
		#plot the training data and fitted regression curve
		plt.scatter(self.stock_days, self.stock_close_prices, color='blue', label='data')
		plt.plot(self.stock_days, self.model.predict(self.stock_days), color="red",  linewidth=2.5, linestyle="-", label='model')
		plt.legend(loc='upper right', frameon=True)
		plt.title('Polynomial regression of stock data')
		plt.ylabel('Stock price ($)')
		plt.xlabel('Operating days since %s' %(self.first_day))
		plt.xticks(range(0, len(self.stock_days), 7))
		plt.show()


	def predict(self):
		#ask for user input
		days_from_now = raw_input('Enter the number of stock market operating days from now that you wish to predict the stock price for: ')
		try:
			days_from_now = int(days_from_now)
		except ValueError as v:
			print 'Error: %s' % (v)

		#print the prediction
		print 'Prediction of stock price %d operating days from now: $%.2f' %(days_from_now, self.model.predict(days_from_now))

#sample execution
myStock = StockScraper()
myStock.get_url()
myStock.scrape()
myStock.plot()
myStock.predict()

