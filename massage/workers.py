from .models import chartofaccounts, service_category, serviceInfo, companyInfo, journalmain, journalcollections, employees, logs
import json, os, decimal, re
from django.core.exceptions import ObjectDoesNotExist, ValidationError
from django.db.models import Sum, Count, Case, When, IntegerField, Q, F, Value
from datetime import datetime
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

#converter
class converter:
	def dateconvert(self,date):
		try:

			self.date = date
			if date is not None:
				self.newDateformat = datetime.strptime(self.date,'%m/%d/%Y')
				newDate = self.newDateformat.strftime('%Y-%m-%d')
			else:
				newDate = datetime.now()

			return newDate

		except ValidationError:
			return self.date
			
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

			self.convert = converter()
			self.startdate = self.convert.dateconvert(startdate)
			self.enddate = self.convert.dateconvert(enddate)
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
  def __init__(self,startdate=None,enddate=None):
  	self.objects = databaseobjects()
  	self.gross = self.objects.gross()
  	self.expense = self.objects.expense()
  	self.convert = converter()
  	self.startdate = self.convert.dateconvert(startdate)
  	self.enddate = self.convert.dateconvert(enddate)

  def netincome(self):
  	grossIncome = 0.00

  	for x in self.gross:
  		grossIncome = decimal.Decimal(grossIncome) + (x.credits - x.debits)

  	expenses = 0.00

  	for x in self.expense:
  		expenses = decimal.Decimal(expenses) + (x.debits - x.credits)

  	netIncome = decimal.Decimal(grossIncome) - decimal.Decimal(expenses)

  	return netIncome,grossIncome,expenses,self.gross,self.expense

  def datedincome(self):
  	totalexpense = journalcollections.objects.filter(transaction_date__gte=self.startdate,\
  		transaction_date__lte=self.enddate,account_id__account_type="Expenses").order_by(\
  		'account_id__account_number')

  	grossincome = journalcollections.objects.filter(transaction_date__gte=self.startdate,\
  		transaction_date__lte=self.enddate,account_id__account_type="Income").order_by(\
  		'account_id__account_number')

  	grossIncome = 0.00
  	expenses = 0.00

  	for x in totalexpense:
  		expenses = decimal.Decimal(expenses) + (x.debits - x.credits)

  	for x in grossincome:
  		grossIncome = decimal.Decimal(grossIncome) + (x.credits - x.debits)

  	netIncome = decimal.Decimal(grossIncome) - decimal.Decimal(expenses)

  	return netIncome

  def incomestatement(self):

  	self.totalexpense = journalcollections.objects.filter(transaction_date__gte=self.startdate,\
  		transaction_date__lte=self.enddate,account_id__account_type="Expenses").order_by(\
  		'account_id__account_number')

  	self.grossincome = journalcollections.objects.filter(transaction_date__gte=self.startdate,\
  		transaction_date__lte=self.enddate,account_id__account_type="Income").order_by(\
  		'account_id__account_number')


  	incomecr = 0.00
  	for x in self.grossincome:
  		incomecr = decimal.Decimal(incomecr) + (x.credits - x.debits)

  	expensedr = 0.00
  	for x in self.totalexpense:
  		expensedr = decimal.Decimal(expensedr) + (x.debits - x.credits)

  	net = decimal.Decimal(incomecr) - decimal.Decimal(expensedr)

  	context = {"incomecr": incomecr,"expensedr":expensedr,
				"netincome":net,"income":self.grossincome,
				"expenses":self.totalexpense}
  	return context

#CLASS FOR TRIAL BALANCE
class Trialbalance:

	def trialbalance(self,startdate,enddate):

		try:

			trialBalance = []
			self.objects = databaseobjects()
			self.convert = converter()
			self.startdate = self.convert.dateconvert(startdate)
			self.enddate = self.convert.dateconvert(enddate)

			self.Journals = journalcollections.objects.filter(
				transaction_date__gte=self.startdate,
				transaction_date__lte=self.enddate
				).values(
				'account_id__account_name',
				'account_id__account_number').distinct()

			self.creditsTotal = journalcollections.objects.filter(
				transaction_date__gte=self.startdate,
				transaction_date__lte=self.enddate
				).aggregate(credits=Sum('credits'))

			self.debitsTotal = journalcollections.objects.filter(
				transaction_date__gte=self.startdate,
				transaction_date__lte=self.enddate
				).aggregate(debits=Sum('debits'))

			for x in self.Journals:
			
				creditstotal = journalcollections.objects.filter(
					account_id__account_number=x['account_id__account_number'],
					transaction_date__gte=self.startdate,
					transaction_date__lte=self.enddate
					).aggregate(credits=Sum('credits'))
			
				debitstotal = journalcollections.objects.filter(
					account_id__account_number=x['account_id__account_number'],
					transaction_date__gte=self.startdate,
					transaction_date__lte=self.enddate
					).aggregate(debits=Sum('debits'))
			
				newList = {
					"name":x['account_id__account_name'],
					"number":x['account_id__account_number'],
					"credits":creditstotal['credits'],
					"debits":debitstotal['debits']
				}

				trialBalance.append(newList)

			context = {
				"Startdate":self.startdate,
				"Endate":self.enddate,
				"journals":trialBalance,
				"debitstotal":self.debitsTotal['debits'],
				"creditstotal":self.creditsTotal['credits'],
			}

			return context

		except ObjectDoesNotExist:
			context = {"Startdate":self.startdate, "Endate":self.enddate}
			return context

#CLASS FOR LEDGERING
class Ledgering:

	def ledgering(self,startdate,enddate,accountnum):

		try:

			ledgerDict = []
			balance = 0.00
			balance = decimal.Decimal(balance)
			self.accountnum = accountnum
			self.startdate = converter().dateconvert(startdate)
			self.enddate = converter().dateconvert(enddate)

			rowCount = journalcollections.objects.filter(
				transaction_date__gte=self.startdate,
				transaction_date__lte=self.enddate,
				account_id__account_number=self.accountnum
				).count()

			ledgerReports = journalcollections.objects.filter(
				transaction_date__gte=self.startdate,
				transaction_date__lte=self.enddate,
				account_id__account_number=self.accountnum
				).order_by('account_id__account_number')
			
			for x in ledgerReports:

				balance = balance + (x.debits - x.credits)

				newList = {

					'transaction_date':x.transaction_date,
					'account_type': x.account_id.account_type, 
					'account_name': x.account_id.account_name, 
					'account_detailtype':x.account_id.account_detailtype,
					'account_number':x.account_id.account_number,
					'debits':x.debits,
					'credits':x.credits,
					'balance':balance
				}

				ledgerDict.append(newList)

			context = {
				"journals": ledgerDict,
				"rowCount":rowCount,
				"chart": databaseobjects().chartofaccs(),
				'startdate':self.startdate,
				"endate":self.enddate
			}

			return context

		except ObjectDoesNotExist:

			context = {"Startdate":self.startdate, "Endate":self.enddate}
			return context

#CLASS FOR BALANCESHEET
class balanceSheet:

	def balancing(self,startdate,enddate,acctype):
		try:


			self.startdate = converter().dateconvert(startdate)
			self.enddate = converter().dateconvert(enddate)
			self.acctype = acctype
			self.income = Net(startdate,enddate)
			assets = []

			currAsset = journalcollections.objects.filter(
				transaction_date__gte=self.startdate,
				transaction_date__lte=self.enddate,
				account_id__account_type=self.acctype
				).values('account_id__account_name',
				'account_id__account_number'
				).distinct()

			for x in currAsset:

				creditsTotal = journalcollections.objects.filter(
					account_id__account_number=x['account_id__account_number'],
					transaction_date__gte=self.startdate,
					transaction_date__lte=self.enddate
					).aggregate(credits=Sum('credits'))

				debitsTotal = journalcollections.objects.filter(
					account_id__account_number=x['account_id__account_number'],
					transaction_date__gte=self.startdate,
					transaction_date__lte=self.enddate
					).aggregate(debits=Sum('debits'))

				accountName = x['account_id__account_name']

				isDepreciation = re.findall("depreciation", accountName.lower())

				isCapital = re.findall("capital", accountName.lower())

				if (isDepreciation):
					total = creditsTotal['credits'] - debitsTotal['debits']

				elif (isCapital):
					total = creditsTotal['credits'] - debitsTotal['debits'] + decimal.Decimal(self.income.datedincome())
					print(self.income.datedincome())
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
			self.startdate = converter().dateconvert(startdate)
			self.enddate = converter().dateconvert(enddate)
			self.acctype = acctype
			self.income = Net(startdate,enddate)
			self.objects = databaseobjects()
			self.capital = 0.00
			self.drawing = 0.00
			currentTotal = 0.00

			currAsset = journalcollections.objects.filter(
				transaction_date__gte=self.startdate,
				transaction_date__lte=self.enddate,
				account_id__account_type=self.acctype
				).order_by('account_id__account_number')

			
			if self.acctype == "Current assets" or self.acctype == "Non-current assets":

				for x in currAsset:
					currentTotal = decimal.Decimal(currentTotal) + (x.debits - x.credits)
		
			elif self.acctype == "Current liabilities" or self.acctype == "Non-current liabilities":

				for x in currAsset:

					currentTotal = decimal.Decimal(currentTotal) + (x.credits - x.debits)

			else:

				equity = self.balancing(startdate,enddate,self.acctype)

				for x in equity:
				
					accountName = x['name']

					isCapital = re.findall("capital", accountName.lower())
					isDrawing = re.findall("drawing", accountName.lower())

					if isCapital:
						self.capital = decimal.Decimal(x['total']) 

					elif isDrawing:
						self.drawing = decimal.Decimal(x['total'])

				currentTotal = decimal.Decimal(self.capital) - decimal.Decimal(self.drawing)

			return currentTotal

		except ObjectDoesNotExist:
			raise e

class Journalize:

	#FUNCTION FOR CREATING JOURNAL RECORDS
	def journalInsert(self,data,date):
		try:
			#GET THE JSON FILE OR CREATE A NEW ONE
			path = os.path.join(BASE_DIR, 'journal.json')
			self.convert = converter()

			#CALL FUNCTION TO CONVERT DATES
			self.startdate = converter().dateconvert(date)
			self.data = data

			#OPEN THE JSON FILE AND WRITE ITS CONTENT
			with open(path, 'w') as data_file:
				data_file.write(self.data)
				data_file.close()

			#CREATE A NEW JOURNAL INSTANCE AND SAVE IT
			create = journalmain(monthof=self.startdate)
			create.save()

			#OPEN THE JSON FILE AND GET ITS CONTENT
			with open(path) as data_file:
				self.data = json.load(data_file)


			#LOOP THROUGH THE DATA
			for x in self.data:

				#GET THE SUM ACCOUNTS IN THE CHART OF ACCOUNTS
				accountCr = chartofaccounts.objects.filter(
					account_number=int(x['accnum'])
					).aggregate(
					totalcreds=Sum('account_credbalance')
					)

				accountDr = chartofaccounts.objects.filter(
					account_number=int(x['accnum'])
					).aggregate(
					totaldebs=Sum('account_debbalance')
					)

				transactionDate = self.convert.dateconvert(x['date'])

				accounts = chartofaccounts.objects.get(account_number=int(x['accnum']))

				#UPDATE CHART OF ACCOUNTS
				chartofaccounts.objects.filter(account_number=int(x['accnum'])).update(
				account_debbalance=decimal.Decimal(accountDr['totaldebs'])+decimal.Decimal(x['deb']))

				chartofaccounts.objects.filter(account_number=int(x['accnum'])).update(
				account_credbalance=decimal.Decimal(accountCr['totalcreds'])+decimal.Decimal(x['cred']))

				#INSERT JOURNAL
				journalize = journalcollections(transaction_date=transactionDate,account_id=accounts,debits=float(x['deb']),
					credits=float(x['cred']),description=x['des'],journalid=create)

				#SAVE THE JOURNAL
				journalize.save()
				
			return "Success"
		except Exception as e:
			print('exception occured')
			context = {"response":e}
			return e

		








