from django.shortcuts import render
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from django.contrib.auth import login, authenticate
from django.db import connection, IntegrityError
from django.utils.html import strip_tags
from django.urls import reverse
from django.core.exceptions import ObjectDoesNotExist
from django.contrib.auth.models import User
from django.db.models import Sum, Count, Case, When, IntegerField, Q, F, Value
from django.db.models.functions import Length, Upper
from .models import chartofaccounts, service_category, serviceInfo, companyInfo, journalmain, journalcollections, employees, logs, journalTotals
import calendar
from datetime import datetime
import json, os, decimal,re
from django.core.files import File
from itertools import chain
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
from .workers import Net, databaseobjects, Trialbalance, Ledgering, balanceSheet
# Create your views here.


def index(request):
	p1 = Net()
	
	context = {"income": p1.netincome()[1],"expense":p1.netincome()[2],"netincome":p1.netincome()[0],"rawincome":p1.netincome()[3],
				"rawexpenses":p1.netincome()[4]}
	return render(request,"massage/index.html",context)

def info(request):
	return render(request,"massage/info.html")

def charts(request):
	
	context = {"chart": chartofaccounts.objects.all()}
	return render(request, "massage/chartsofaccounts.html",context)

#INSERT ACCOUNTS
def insertaccount(request):

	accountnumber = strip_tags(request.POST["number"])

	accountname = strip_tags(request.POST["name"])

	accountType = strip_tags(request.POST["type"])

	accountDetail = strip_tags(request.POST["detail"])

	try:

		add = chartofaccounts(account_number=accountnumber,account_name=accountname,
		account_type=accountType,account_detailtype=accountDetail,account_debbalance=0.00,
		account_credbalance=0.00)

		add.save()

		context = {"response":"Success"}

		return JsonResponse(context)

	except IntegrityError:

		return HttpResponse("Account Already Exist",status=403)

def trialbalance(request):
	objects = databaseobjects()
	context = {"Journals": objects.alljournal()}

	if request.user.is_authenticated:

		if request.method == "POST":

			startdate = request.POST.get("startdate",False)

			enddate = request.POST.get("enddate",False)

			starttime = datetime.strptime(startdate,'%m/%d/%Y')

			endtime = datetime.strptime(enddate,'%m/%d/%Y')

			newstart = starttime.strftime('%Y-%m-%d')

			newend = endtime.strftime('%Y-%m-%d')

			trial = Trialbalance()

			return render(request,"massage/trialbalance.html",trial.trialbalance(newstart,newend))
		else:
			return render(request,"massage/trialbalance.html",context)
	else:
		return HttpResponseRedirect(reverse("index"))

def ledger(request):
	objects = databaseobjects()
	context = {"Journals": objects.alljournal(),"chart": objects.chartofaccs()}
	if request.user.is_authenticated:

		if request.method == "POST":

				startdate = request.POST.get("startdate",False)

				enddate = request.POST.get("enddate",False)

				starttime = datetime.strptime(startdate,'%m/%d/%Y')

				endtime = datetime.strptime(enddate,'%m/%d/%Y')

				newstart = starttime.strftime('%Y-%m-%d')

				newend = endtime.strftime('%Y-%m-%d')

				account = request.POST.get("account",False)

				return render(request,"massage/ledger.html",ledgerring.ledgering(newstart,newend,account))

		else:
			return render(request,"massage/ledger.html",context)
	else:
		return HttpResponseRedirect(reverse("index"))



def balancesheet(request):
	objects = databaseobjects()
	journalList = journalmain.objects.all()
	context = {"Journals": objects.alljournal()}
	if request.user.is_authenticated:

		if request.method == "POST":

			startdate = request.POST.get("startdate",False)

			enddate = request.POST.get("enddate",False)

			starttime = datetime.strptime(startdate,'%m/%d/%Y')

			endtime = datetime.strptime(enddate,'%m/%d/%Y')

			newstart = starttime.strftime('%Y-%m-%d')

			newend = endtime.strftime('%Y-%m-%d')

			accounts = ('Current assets','Non-current assets','Current liabilities',
						'Non-current liabilities',"Owner's equity")
			accounts1 = ('Current assets','Non-current assets','Current liabilities',
						'Non-current liabilities',"Owner's equity")
			context = {}
			balance = balanceSheet()
			for x in accounts:
				context[x.replace(" ","").replace("-","").replace("'","")] = balance.balancing(newstart,newend,x)

			for x in accounts1:
				context[x.replace(" ","").replace("-","").replace("'","")+"totals"] = balance.totals(newstart,newend,x)

			context["totalasset"] = decimal.Decimal(context['Currentassetstotals']) + \
			decimal.Decimal(context['Noncurrentassetstotals'])

			context["totalliabilities"] = decimal.Decimal(context['Noncurrentliabilitiestotals']) + \
			decimal.Decimal(context['Currentliabilitiestotals'])

			context["totalliabilitesandequity"] = (decimal.Decimal(context['Noncurrentliabilitiestotals']) + \
				decimal.Decimal(context['Currentliabilitiestotals']))+(decimal.Decimal(context['Ownersequitytotals']))

			return render(request,"massage/balancesheet.html",context)

		else:
			return render(request,"massage/balancesheet.html",context)
	else:
		return HttpResponseRedirect(reverse("index"))



def incomestatement(request):
	journalList = journalmain.objects.all()
	context = {"Journals": journalList,}
	if request.user.is_authenticated:

		if request.method == "POST":

			try:
				journs = request.POST.get("journs",False)

				expenses = journalcollections.objects.filter(journalid__id=journs).filter(\
						account_id__account_type="Expenses").order_by('account_id__account_number')

				income = journalcollections.objects.filter(journalid__id=journs).filter(\
						account_id__account_type="Income").order_by('account_id__account_number')

				incomecr = 0.00
				expensedr = 0.00

				for x in income:
					incomecr = decimal.Decimal(incomecr) + (x.credits - x.debits)

				for x in expenses:
					expensedr = decimal.Decimal(expensedr) + (x.debits - x.credits)

				context = {	"income":income,"expenses":expenses,"Journals": journalList,"signs": 'True',
							"incomecr":incomecr,"expensedr":expensedr,"netincome":incomecr-expensedr}

				return render(request,"massage/incomestatement.html",context)

			except ObjectDoesNotExist:
				return render(request,"massage/incomestatement.html",context)

		else:
			return render(request,"massage/incomestatement.html",context)

	else:
		return HttpResponseRedirect(reverse("index"))


def receive(request):
	return render(request,"massage/receive.html")


#JOURNALIZE
def journalize(request):
	try:
		maxid = journalmain.objects.all().order_by("-id")[0]

	except IndexError:
		 maxid = 1

	context = {"chart": chartofaccounts.objects.all(),"maxid": maxid}

	return render(request,"massage/journal.html",context)


#INSERT JOURNAL
def inserjournal(request):
	base = 0.00

	path = os.path.join(BASE_DIR, 'journal.json')

	data1 = request.POST["json"]
	basedate = request.POST["basedate"]

	datetimeobject1 = datetime.strptime(basedate,'%m/%d/%Y')
	newformat1 = datetimeobject1.strftime('%Y-%m-%d')

	with open(path, 'w') as data_file:
		data_file.write(data1)
		data_file.close()

	create = journalmain(monthof=newformat1)
	create.save()

	with open(path) as data_file:

		data = json.load(data_file)

		for x in data:

			accounttotalcred = chartofaccounts.objects.filter(account_number=int(x['accnum'])\
				).aggregate(totalcreds=Sum('account_credbalance'))


			accounttotaldeb = chartofaccounts.objects.filter(account_number=int(x['accnum'])\
				).aggregate(totaldebs=Sum('account_debbalance'))


			totals3 = journalTotals.objects.filter(account_id__account_number=int(x['accnum']),
			journalid=create.id).aggregate(totaldebs=Sum('account_debbalance'))
			
			if totals3['totaldebs'] is None:
				totals3['totaldebs'] = base

			totals4 = journalTotals.objects.filter(account_id__account_number=int(x['accnum']),
			journalid=create.id).aggregate(totalcreds=Sum('account_credbalance'))
			
			if totals4['totalcreds'] is None:
				totals4['totalcreds'] = base

			datetimeobject = datetime.strptime(x['date'],'%m/%d/%Y')

			newformat = datetimeobject.strftime('%Y-%m-%d')

			chartofaccs = chartofaccounts.objects.get(account_number=int(x['accnum']))

			journalTotals.objects.update_or_create(
			account_id=chartofaccs,journalid=create,
			defaults={'account_number':x['accnum'],
			'account_debbalance': decimal.Decimal(totals3['totaldebs'])+decimal.Decimal(x['deb']),
			'account_credbalance': decimal.Decimal(totals4['totalcreds'])+decimal.Decimal(x['cred'])},)
			
			chartofaccounts.objects.filter(account_number=int(x['accnum'])).update(
			account_debbalance=decimal.Decimal(accounttotaldeb['totaldebs'])+decimal.Decimal(x['deb']))
			
			chartofaccounts.objects.filter(account_number=int(x['accnum'])).update(
			account_credbalance=decimal.Decimal(accounttotalcred['totalcreds'])+decimal.Decimal(x['cred']))
			
			add = journalcollections(transaction_date=newformat,account_id=chartofaccs,debits=float(x['deb']),
			credits=float(x['cred']),description=x['des'],journalid=create)

			add.save()

			#print(connection.queries)

	context = {"response":"Success"}

	return JsonResponse(context)
	#SIGNUP
def sign_up(request):
	if request.user.is_authenticated:
		return HttpResponseRedirect(reverse("index"))
	else:
		if request.method == "POST":
			username = strip_tags(request.POST["username"])
			email = strip_tags(request.POST["email"])
			password = strip_tags(request.POST["password"])
			fname = strip_tags(request.POST["fname"])
			lname = strip_tags(request.POST["lname"])
			try:
				user = User.objects.create_user(username, email, password)
				user.first_name = fname
				user.last_name = lname
				user.save()
				user1 = authenticate(request, username=username, password=password)
				login(request, user)
				return HttpResponseRedirect(reverse("index"))
			except IntegrityError:
				pass
		else:
			return render(request, "massage/signup.html")