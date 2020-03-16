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

	def getJournalInfo(self,accID):
		self.id = accID
		self.Journals = journalcollections.objects.filter(journalid__id=self.id)
		accs = []
		for x in self.Journals:
			case = {"id":x.id,"date":x.transaction_date,"name":x.account_id.account_name,"number":x.account_id.account_number,\
					"description":x.description,"credits":x.credits,"debits":x.debits}
			accs.append(case)
		return accs


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

	def infocompany(self):
		self.company = companyInfo.objects.all()
		print(self.company)
		return self.company

#CLASS FOR CALCULATING NET INCOME
class Net:
  def __init__(self,startdate,enddate):
  	self.objects = databaseobjects()
  	self.gross = self.objects.gross()
  	self.expense = self.objects.expense()
  	self.convert = converter()
  	self.startdate = self.convert.dateconvert(startdate)
  	self.enddate = self.convert.dateconvert(enddate)

  def netincome(self):
  	incomecr = 0.00
  	for x in self.gross:
  		incomecr = decimal.Decimal(incomecr) + (x.credits - x.debits)
  	expensedr = 0.00
  	for x in self.expense:
  		expensedr = decimal.Decimal(expensedr) + (x.debits - x.credits)
  	net = decimal.Decimal(incomecr) - decimal.Decimal(expensedr)
  	return net,incomecr,expensedr,self.gross,self.expense

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
			self.objects = databaseobjects()
			accountsum = []
			self.convert = converter()
			self.startdate = self.convert.dateconvert(startdate)
			self.enddate = self.convert.dateconvert(enddate)
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
			self.convert = converter()
			self.startdate = self.convert.dateconvert(startdate)
			self.enddate = self.convert.dateconvert(enddate)
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
			self.convert = converter()
			self.startdate = self.convert.dateconvert(startdate)
			self.enddate = self.convert.dateconvert(enddate)
			self.acctype = acctype
			self.income = Net(startdate,enddate)
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
					total = decimal.Decimal(creditsTotal['credits']) - decimal.Decimal(debitsTotal['debits']) + decimal.Decimal(self.income.netincome()[0])
				else:
					total = decimal.Decimal(debitsTotal['debits']) - decimal.Decimal(creditsTotal['credits'])

				case = {"name":x['account_id__account_name'],"number":x['account_id__account_number'],\
						"total":total}

				assets.append(case)
			return assets
		except ObjectDoesNotExist as e:
			raise e

	def totals(self,startdate,enddate,acctype):
		try:
			self.convert = converter()
			self.startdate = self.convert.dateconvert(startdate)
			self.enddate = self.convert.dateconvert(enddate)
			self.acctype = acctype
			self.income = Net(startdate,enddate)
			self.objects = databaseobjects()
			self.capital = 0.00
			self.drawing = 0.00
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

				equity = self.balancing(startdate,enddate,self.acctype)

				for x in equity:
				
					accountName = x['name']

					isCapital = re.findall("capital", accountName.lower())
					isDrawing = re.findall("drawing", accountName.lower())

					if isCapital:
						self.capital = decimal.Decimal(x['total']) 

					elif isDrawing:
						self.drawing = x['total']


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

			#CALL FUNCTION TO CONVERT DATES
			self.convert = converter()
			self.startdate = self.convert.dateconvert(date)
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
				accountCr = chartofaccounts.objects.filter(account_number=int(x['accnum'])\
					).aggregate(totalcreds=Sum('account_credbalance'))
				accountDr = chartofaccounts.objects.filter(account_number=int(x['accnum'])\
					).aggregate(totaldebs=Sum('account_debbalance'))

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

		

class companysClass:

	def comInfo(self,q,w,e,r,t,y,u):
		try:
			self.q = q
			self.w = w
			self.e = e
			self.r = r
			self.t = t
			self.y = y
			self.u = u
			print(self.u)
			print("IM AT CLASS")

			companyInfo.objects.update_or_create(
				id=1,defaults={'company_name':self.q,"company_phone":self.w,
				"company_fax":self.e,"company_country":self.r,"company_city":self.t,
				"company_state":self.y,"company_zip":self.u},
				)
			context ={"response":"Succes"}
			return "context"
		except Exception as e:
			return HttpResponse(e,status=403)
		
		

		







