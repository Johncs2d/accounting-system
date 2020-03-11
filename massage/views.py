from django.shortcuts import render
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from django.contrib.auth import login, authenticate
from django.db import connection, IntegrityError
from django.utils.html import strip_tags
from django.core.exceptions import ObjectDoesNotExist
from django.contrib.auth.models import User
from django.db.models import Sum, Count, Case, When, IntegerField
from .models import chartofaccounts, service_category, serviceInfo, companyInfo, journalmain, journalcollections, employees, logs
# Create your views here.
from datetime import datetime
import json, os, decimal
from django.core.files import File
from itertools import chain
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def index(request):
	x = journalcollections.objects.values('id','account_id__account_number','account_id__account_name',
		'account_id__account_type','account_id__account_type','account_id__account_detailtype',
		'account_id__account_debbalance','account_id__account_credbalance').distinct().filter(transaction_date__gte='2020-03-01',
		transaction_date__lte='2020-03-31').filter(account_id__account_number__lt=200)
	
	for y in x:
		totals = journalcollections.objects.filter(pk=y['id']).aggregate(totalcreds=Sum('account_id__account_credbalance'))
		print(totals['totalcreds'])
	return render(request,"massage/index.html")

def info(request):
	return render(request,"massage/info.html")

def charts(request):
	
	context = {"chart": chartofaccounts.objects.all()}
	return render(request, "massage/chartsofaccounts.html",context)

def insertaccount(request):
	accountnumber = strip_tags(request.POST["number"])
	accountname = strip_tags(request.POST["name"])
	accountType = strip_tags(request.POST["type"])
	accountDetail = strip_tags(request.POST["detail"])
	try:
		add = chartofaccounts(account_number=accountnumber,account_name=accountname,
			account_type=accountType,account_detailtype=accountDetail,account_debbalance=0.00,account_credbalance=0.00)
		add.save()
		context = {"response":"Success"}
		return JsonResponse(context)
	except IntegrityError:
		return HttpResponse("Account Already Exist",status=403)
def trialbalance(request):
	return render(request,"massage/trialbalance.html")

def ledger(request):
	return render(request,"massage/ledger.html")

def balancesheet(request):
	return render(request,"massage/balancesheet.html")

def incomestatement(request):
	return render(request,"massage/incomestatement.html")

def receive(request):
	return render(request,"massage/receive.html")

def journalize(request):
	try:
		maxid = journalmain.objects.all().order_by("-id")[0]
	except IndexError:
		 maxid = 1
	context = {"chart": chartofaccounts.objects.all(),
			   "maxid": maxid
			   }
	return render(request,"massage/journal.html",context)

def inserjournal(request):
	data1 = request.POST["json"]
	f = open(os.path.join(BASE_DIR, 'journal.json'), 'w')
	f.write(data1)
	f.close()
	create = journalmain()
	create.save()
	with open(os.path.join(BASE_DIR, 'journal.json')) as data_file:
		data = json.load(data_file)
		for x in data:
			totals1 = journalcollections.objects.filter(account_id__account_number=int(x['accnum'])).aggregate(totalcreds=Sum('account_id__account_credbalance'))
			totals2 = journalcollections.objects.filter(account_id__account_number=int(x['accnum'])).aggregate(totaldebs=Sum('account_id__account_debbalance'))
			datetimeobject = datetime.strptime(x['date'],'%m/%d/%Y')
			newformat = datetimeobject.strftime('%Y-%m-%d')
			chartofaccs = chartofaccounts.objects.get(account_number=int(x['accnum']))
			chartofaccounts.objects.filter(account_number=int(x['accnum'])).update(account_debbalance=decimal.Decimal(totals2['totaldebs'])+decimal.Decimal(x['deb']))
			chartofaccounts.objects.filter(account_number=int(x['accnum'])).update(account_credbalance=decimal.Decimal(totals1['totalcreds'])+decimal.Decimal(x['cred']))
			add = journalcollections(transaction_date=newformat,account_id=chartofaccs,debits=float(x['deb']),credits=float(x['cred']),description=x['des'],journalid=create)

			add.save()
	context = {"response":"Success"}
	return JsonResponse(context)
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