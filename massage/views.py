from django.shortcuts import render
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from django.contrib.auth import login, authenticate
from django.db import connection, IntegrityError
from django.utils.html import strip_tags
from django.core.exceptions import ObjectDoesNotExist
from django.contrib.auth.models import User
from django.db.models import Sum, Count, Case, When, IntegerField, Q
from .models import chartofaccounts, service_category, serviceInfo, companyInfo, journalmain, journalcollections, employees, logs, journalTotals
# Create your views here.
from datetime import datetime
import json, os, decimal
from django.core.files import File
from itertools import chain
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def index(request):

	# for y in x:
	# 	# totals = journalcollections.objects.filter(pk=y['id']).aggregate(totalcreds=Sum('account_id__account_credbalance'))
	# 	print(y)
	return render(request,"massage/index.html")

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

	context = {"Journals": journalmain.objects.all()}

	if request.user.is_authenticated:

		if request.method == "POST":

			startdate = request.POST.get("startdate",False)
			enddate = request.POST.get("enddate",False)
			
			
			try:
				

				if startdate is not False:
					
					
					starttime = datetime.strptime(startdate,'%m/%d/%Y')

					endtime = datetime.strptime(enddate,'%m/%d/%Y')

					newstart = starttime.strftime('%Y-%m-%d')

					newend = endtime.strftime('%Y-%m-%d')

					context = {"journals": journalTotals.objects.filter(journalid__datecreated__gte=newstart,
								journalid__datecreated__lte=newend).order_by('account_id__account_number'),
								"Startdate":startdate,
								"Endate":enddate,
								"Journals": journalmain.objects.all(),
								"signs": 'True'}
				else:

					journs = request.POST.get("journs",False)

					context = {"journals": journalTotals.objects.filter(journalid__id=journs).order_by('account_id__account_number'),
							   "Journals": journalmain.objects.all(),
							   "signs": 'True'}



				return render(request,"massage/trialbalance.html",context)

			except ObjectDoesNotExist:

				return render(request,"massage/trialbalance.html",context)

		else:
			return render(request,"massage/trialbalance.html",context)
	else:
		return HttpResponseRedirect(reverse("index"))
			
	

def ledger(request):
	context = {"Journals": journalmain.objects.all(),
			   }
	if request.user.is_authenticated:

		if request.method == "POST":

			
			
			try:
				journalList = journalmain.objects.all()
				startdate = request.POST.get("startdate",False)
				enddate = request.POST.get("enddate",False)
				print(startdate)
				print(enddate)
				if startdate is not False:
					
					starttime = datetime.strptime(startdate,'%m/%d/%Y')

					endtime = datetime.strptime(enddate,'%m/%d/%Y')

					newstart = starttime.strftime('%Y-%m-%d')

					newend = endtime.strftime('%Y-%m-%d')

					rowCount = journalcollections.objects.filter(transaction_date__gte=newstart,
								transaction_date__lte=newend).count()

					totaldebit = journalcollections.objects.filter(transaction_date__gte=newstart,
								transaction_date__lte=newend).aggregate(totaldebs=Sum('debits'))

					totalcredit = journalcollections.objects.filter(transaction_date__gte=newstart,
								transaction_date__lte=newend).aggregate(totalcreds=Sum('credits'))
					str(totalcredit.query)

					if totaldebit['totaldebs'] is not None:
						finaltotal = decimal.Decimal(totaldebit['totaldebs'])
					else:
						finaltotal = 0.00

					if totalcredit['totalcreds'] is not None:
						finaltotal1 = decimal.Decimal(totalcredit['totalcreds'])
					else:
						finaltotal1 = 0.00
					

					rangedJournal = journalcollections.objects.filter(transaction_date__gte=newstart,
									transaction_date__lte=newend).order_by('account_id__account_number')

					context = {"journals": rangedJournal,
								"Startdate":startdate,
								"Endate":enddate,
								"Journals": journalList,
								"creditstotal":finaltotal1,
								"debitstotal":finaltotal,
								"rowCount":rowCount,
								"signs": 'True'
								}
				else:

					journs = request.POST.get("journs",False)

					rowCount = journalcollections.objects.filter(journalid__id=journs).count()
					
					totaldebit = journalcollections.objects.filter(journalid__id=journs).aggregate(totaldebs=Sum('debits'))
					
					totalcredit = journalcollections.objects.filter(journalid__id=journs).aggregate(totalcreds=Sum('credits'))

					filteredJournal = journalcollections.objects.filter(journalid__id=journs).order_by('account_id__account_number')
					

					if totaldebit['totaldebs'] is not None:
						finaltotal = decimal.Decimal(totaldebit['totaldebs'])
					else:
						finaltotal = 0.00

					if totalcredit['totalcreds'] is not None:
						finaltotal1 = decimal.Decimal(totalcredit['totalcreds'])
					else:
						finaltotal1 = 0.00


					context = {"journals": filteredJournal,
							   "Journals": journalList,
							   "creditstotal":finaltotal1,
								"debitstotal":finaltotal,
								"rowCount":rowCount,
								"signs": 'True'
								}

				return render(request,"massage/ledger.html",context)

			except ObjectDoesNotExist:

				return render(request,"massage/ledger.html",context)

		else:
			return render(request,"massage/ledger.html",context)
	else:
		return HttpResponseRedirect(reverse("index"))


def balancesheet(request):

	context = {"Journals": journalmain.objects.all(),
			   }
	if request.user.is_authenticated:

		if request.method == "POST":

			
			
			try:
				journalList = journalmain.objects.all()
				startdate = request.POST.get("startdate",False)
				enddate = request.POST.get("enddate",False)
				print(startdate)
				print(enddate)
				if startdate is not False:
					
					starttime = datetime.strptime(startdate,'%m/%d/%Y')

					endtime = datetime.strptime(enddate,'%m/%d/%Y')

					newstart = starttime.strftime('%Y-%m-%d')

					newend = endtime.strftime('%Y-%m-%d')

					current_assets = journalcollections.objects.filter(transaction_date__gte=newstart,
								transaction_date__lte=newend).filter(account_id__account_type='Current assets')\
								.order_by('account_id__account_number')

					current_assets_total = journalcollections.objects.filter(transaction_date__gte=newstart,
								transaction_date__lte=newend).filter(account_id__account_type='Current assets')\
								.aggregate(totalcreds=Sum('credits'))

					nonCurrent_assets = journalcollections.objects.filter(transaction_date__gte=newstart,
								transaction_date__lte=newend).filter(Q(account_id__account_type='Fixed assets')\
								|Q(account_id__account_type='Non-current assets')).order_by('account_id__account_number')
								
					


					if totaldebit['totaldebs'] is not None:
						finaltotal = decimal.Decimal(totaldebit['totaldebs'])
					else:
						finaltotal = 0.00

					if totalcredit['totalcreds'] is not None:
						finaltotal1 = decimal.Decimal(totalcredit['totalcreds'])
					else:
						finaltotal1 = 0.00
					

					rangedJournal = journalcollections.objects.filter(transaction_date__gte=newstart,
									transaction_date__lte=newend).order_by('account_id__account_number')

					context = {"journals": rangedJournal,
								"Startdate":startdate,
								"Endate":enddate,
								"Journals": journalList,
								"creditstotal":finaltotal1,
								"debitstotal":finaltotal,
								"rowCount":rowCount,
								"signs": 'True'
								}
				else:

					journs = request.POST.get("journs",False)

					rowCount = journalcollections.objects.filter(journalid__id=journs).count()
					
					totaldebit = journalcollections.objects.filter(journalid__id=journs).aggregate(totaldebs=Sum('debits'))
					
					totalcredit = journalcollections.objects.filter(journalid__id=journs).aggregate(totalcreds=Sum('credits'))

					filteredJournal = journalcollections.objects.filter(journalid__id=journs).order_by('account_id__account_number')
					

					if totaldebit['totaldebs'] is not None:
						finaltotal = decimal.Decimal(totaldebit['totaldebs'])
					else:
						finaltotal = 0.00

					if totalcredit['totalcreds'] is not None:
						finaltotal1 = decimal.Decimal(totalcredit['totalcreds'])
					else:
						finaltotal1 = 0.00


					context = {"journals": filteredJournal,
							   "Journals": journalList,
							   "creditstotal":finaltotal1,
								"debitstotal":finaltotal,
								"rowCount":rowCount,
								"signs": 'True'
								}

				return render(request,"massage/balancesheet.html",context)

			except ObjectDoesNotExist:

				return render(request,"massage/balancesheet.html",context)

		else:
			return render(request,"massage/balancesheet.html",context)
	else:
		return HttpResponseRedirect(reverse("index"))

def incomestatement(request):
	return render(request,"massage/incomestatement.html")

def receive(request):
	return render(request,"massage/receive.html")
	#JOURNALIZE
def journalize(request):
	try:
		maxid = journalmain.objects.all().order_by("-id")[0]
	except IndexError:
		 maxid = 1
	context = {"chart": chartofaccounts.objects.all(),
			   "maxid": maxid
			   }
	return render(request,"massage/journal.html",context)
	#INSERT JOURNAL
def inserjournal(request):
	base = 0.00

	path = os.path.join(BASE_DIR, 'journal.json')

	data1 = request.POST["json"]

	f = open(path, 'w')

	f.write(data1)

	f.close()

	create = journalmain()

	create.save()

	with open(path) as data_file:

		data = json.load(data_file)

		for x in data:

			totals1 = journalcollections.objects.filter(account_id__account_number=int(x['accnum']),
			journalid=create.id).aggregate(totalcreds=Sum('account_id__account_credbalance'))

			if totals1['totalcreds'] is None:
				totals1['totalcreds'] = base;

			totals2 = journalcollections.objects.filter(account_id__account_number=int(x['accnum']),
			journalid=create.id).aggregate(totaldebs=Sum('account_id__account_debbalance'))
			
			if totals2['totaldebs'] is None:
				totals2['totaldebs'] = base;

			totals3 = journalTotals.objects.filter(account_id__account_number=int(x['accnum']),
			journalid=create.id).aggregate(totaldebs=Sum('account_debbalance'))
			
			if totals3['totaldebs'] is None:
				totals3['totaldebs'] = base;

			totals4 = journalTotals.objects.filter(account_id__account_number=int(x['accnum']),
			journalid=create.id).aggregate(totalcreds=Sum('account_credbalance'))
			
			if totals4['totalcreds'] is None:
				totals4['totalcreds'] = base;

			datetimeobject = datetime.strptime(x['date'],'%m/%d/%Y')

			newformat = datetimeobject.strftime('%Y-%m-%d')

			chartofaccs = chartofaccounts.objects.get(account_number=int(x['accnum']))

			obj, created = journalTotals.objects.update_or_create(
			account_id=chartofaccs,journalid=create,
			defaults={'account_number':x['accnum'],
			'account_debbalance': decimal.Decimal(totals3['totaldebs'])+decimal.Decimal(x['deb']),
			'account_credbalance': decimal.Decimal(totals4['totalcreds'])+decimal.Decimal(x['cred'])},)
			
			chartofaccounts.objects.filter(account_number=int(x['accnum'])).update(
			account_debbalance=decimal.Decimal(totals2['totaldebs'])+decimal.Decimal(x['deb']))
			
			chartofaccounts.objects.filter(account_number=int(x['accnum'])).update(
			account_credbalance=decimal.Decimal(totals1['totalcreds'])+decimal.Decimal(x['cred']))
			
			add = journalcollections(transaction_date=newformat,account_id=chartofaccs,debits=float(x['deb']),
			credits=float(x['cred']),description=x['des'],journalid=create)

			add.save()

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