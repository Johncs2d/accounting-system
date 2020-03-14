from .models import chartofaccounts, service_category, serviceInfo, companyInfo, journalmain, journalcollections, employees, logs, journalTotals
import json, os, decimal, re
from django.core.exceptions import ObjectDoesNotExist
from django.db.models import Sum, Count, Case, When, IntegerField, Q, F, Value

#DATABASE OBJECTS
class databaseobjects:
	def gross(self):
		self.grossincome = journalcollections.objects.filter(account_id__account_type="Income"\
		).order_by('account_id__account_number')
		return self.grossincome

	def expense(self):
		self.totalexpense = journalcollections.objects.filter(account_id__account_type="Expenses"\
		).order_by('account_id__account_number')
		return self.totalexpense

	def alljournal(self):
		self.Journals = journalmain.objects.all()
		return self.Journals

	def chartofaccs(self):
		self.chart = chartofaccounts.objects.all()
		return self.chart
	def drawing(self,startdate,enddate):
		try:

			self.startdate = startdate
			self.enddate = enddate
			self.accounts = self.chartofaccs()
		
			for x in self.accounts:
				accountName = x.account_name
				isDrawing = re.findall("drawing", accountName.lower())
				if isDrawing:
					self.drawingcr = journalcollections.objects.filter(transaction_date__gte=self.startdate,\
						transaction_date__lte=self.enddate,account_id__account_number=x.account_number\
						).aggregate(credits=Sum('credits'))

					self.drawingdr = journalcollections.objects.filter(transaction_date__gte=self.startdate,\
						transaction_date__lte=self.enddate,account_id__account_number=x.account_number\
						).aggregate(debits=Sum('debits'))
			if self.drawingcr['credits'] is None:
				self.drawingcr['credits'] = 0

			if self.drawingdr['debits'] is None:
				self.drawingdr['debits'] = 0
			return decimal.Decimal(self.drawingdr['debits']) - decimal.Decimal(self.drawingcr['credits'])
		except ObjectDoesNotExist:
			return 0
		

		
		

#CLASS FOR CALCULATING NET INCOME
class Net:
  def __init__(self):
  	self.objects = databaseobjects()
  	self.gross = self.objects.gross()
  	self.expense = self.objects.expense()

  def netincome(self):
  	incomecr = 0.00
  	for x in self.gross:
  		incomecr = decimal.Decimal(incomecr) + (x.credits - x.debits)
  	expensedr = 0.00
  	for x in self.expense:
  		expensedr = decimal.Decimal(expensedr) + (x.debits - x.credits)
  	net = incomecr - expensedr
  	return net,incomecr,expensedr,self.gross,self.expense

#CLASS FOR TRIAL BALANCE
class Trialbalance:
	def trialbalance(self,startdate,enddate):
		try:
			self.objects = databaseobjects()
			accountsum = []
			self.startdate = startdate
			self.enddate = enddate
			self.Journals = journalcollections.objects.filter(transaction_date__gte=self.startdate,
				transaction_date__lte=self.enddate).values('account_id__account_name',\
				'account_id__account_number').distinct()

			self.creditsTotal = journalcollections.objects.filter(transaction_date__gte=self.startdate,\
				transaction_date__lte=self.enddate).aggregate(credits=Sum('credits'))

			self.debitsTotal = journalcollections.objects.filter(transaction_date__gte=self.startdate,\
				transaction_date__lte=self.enddate).aggregate(debits=Sum('debits'))
			for x in self.Journals:
			
				creditstotal = journalcollections.objects.filter(account_id__account_number=x['account_id__account_number']\
					,transaction_date__gte=self.startdate,transaction_date__lte=self.enddate).aggregate(credits=Sum('credits'))
			
				debitstotal = journalcollections.objects.filter(account_id__account_number=x['account_id__account_number']\
					,transaction_date__gte=self.startdate,transaction_date__lte=self.enddate).aggregate(debits=Sum('debits'))
			
				case = {"name":x['account_id__account_name'],"number":x['account_id__account_number'],\
					"credits":creditstotal['credits'],"debits":debitstotal['debits']}
			
				accountsum.append(case)
			context = {"Journals":self.objects.alljournal(),"Startdate":self.startdate,
							"Endate":self.enddate,"journals":accountsum,"debitstotal":self.debitsTotal['debits'],
							"creditstotal":self.creditsTotal['credits'],"signs": 'True'}
			return context
		except ObjectDoesNotExist:
			context = {"Startdate":self.startdate, "Endate":self.enddate}
			return context

#CLASS FOR LEDGERING
class Ledgering:
	def ledgering(self,startdate,enddate,accountnum):
		try:
			self.startdate = startdate
			self.enddate = enddate
			self.accountnum = accountnum
			self.objects = databaseobjects()
			rowCount = journalcollections.objects.filter(transaction_date__gte=self.startdate,
				transaction_date__lte=self.enddate,account_id__account_number=self.accountnum).count()

			filteredJournal = journalcollections.objects.filter(transaction_date__gte=self.startdate,
				transaction_date__lte=self.enddate,account_id__account_number=self.accountnum\
				).order_by('account_id__account_number')

			journaldict = []

			balance = 0.00
			for x in filteredJournal:

				balance = decimal.Decimal(balance) + (x.debits - x.credits)

				case = {'transaction_date':x.transaction_date,'account_type': x.account_id.account_type, 
						'account_name': x.account_id.account_name, 'account_detailtype':x.account_id.account_detailtype,
						'account_number':x.account_id.account_number,'debits':x.debits,
						'credits':x.credits,'balance':balance}

				journaldict.append(case)

			context = {"journals": journaldict,"Journals": self.objects.alljournal(),
							"rowCount":rowCount,"chart": self.objects.chartofaccs(),
							'startdate':self.startdate,"endate":self.enddate}

			return context

		except ObjectDoesNotExist:
			context = {"Startdate":self.startdate, "Endate":self.enddate}
			return context

#CLASS FOR BALANCESHEET
class balanceSheet:

	def balancing(self,startdate,enddate,acctype):
		try:
			self.startdate = startdate
			self.enddate = enddate
			self.acctype = acctype
			self.income = Net()
			assets = []

			currAsset = journalcollections.objects.filter(transaction_date__gte=self.startdate,transaction_date__lte=\
				self.enddate,account_id__account_type=self.acctype).values('account_id__account_name',\
				'account_id__account_number').distinct()

			for x in currAsset:

				creditsTotal = journalcollections.objects.filter(account_id__account_number=x[\
					'account_id__account_number'],transaction_date__gte=self.startdate,transaction_date__lte=\
					self.enddate).aggregate(credits=Sum('credits'))

				debitsTotal = journalcollections.objects.filter(account_id__account_number=x[\
					'account_id__account_number'],transaction_date__gte=self.startdate,transaction_date__lte=\
					self.enddate).aggregate(debits=Sum('debits'))

				accountName = x['account_id__account_name']

				isDepreciation = re.findall("depreciation", accountName.lower())
				isCapital = re.findall("capital", accountName.lower())
				if (isDepreciation):
					total = creditsTotal['credits'] - debitsTotal['debits']

				elif (isCapital):
					total = creditsTotal['credits'] - debitsTotal['debits'] + self.income.netincome()[0]
				else:
					total = debitsTotal['debits'] - creditsTotal['credits']

				case = {"name":x['account_id__account_name'],"number":x['account_id__account_number'],\
						"total":total}

				assets.append(case)
			return assets
		except ObjectDoesNotExist as e:
			raise e

	def totals(self,startdate,enddate,acctype):
		try:
			self.startdate = startdate
			self.enddate = enddate
			self.acctype = acctype
			self.income = Net()
			self.objects = databaseobjects()
			currAsset = journalcollections.objects.filter(transaction_date__gte=self.startdate,transaction_date__lte=\
				self.enddate,account_id__account_type=self.acctype).order_by('account_id__account_number')
			currentTotal = 0.00
		
			if self.acctype == "Current assets" or self.acctype == "Non-current assets":

				for x in currAsset:
					currentTotal = decimal.Decimal(currentTotal) + (x.debits - x.credits)
		
			elif self.acctype == "Current liabilities" or self.acctype == "Non-current liabilities":

				for x in currAsset:

					currentTotal = decimal.Decimal(currentTotal) + (x.credits - x.debits)
			else:
				for x in currAsset:
				
					accountName = x.account_id.account_name

					isCapital = re.findall("capital", accountName.lower())
					isDrawing = re.findall("drawing", accountName.lower())

					if isCapital:
						currentTotal = (decimal.Decimal(currentTotal) + (x.credits - x.debits)) + (self.income.netincome()[0] -\
						 self.objects.drawing(self.startdate,self.enddate))
					elif isDrawing:
						currentTotal = (decimal.Decimal(currentTotal) + (x.debits - x.credits))
					else:
						currentTotal = (decimal.Decimal(currentTotal) + (x.credits - x.debits))

			return currentTotal

			
		except ObjectDoesNotExist:
			raise e

		
