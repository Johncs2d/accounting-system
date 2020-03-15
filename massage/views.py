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
from .models import chartofaccounts, service_category, serviceInfo, companyInfo, journalmain, journalcollections, employees, logs
import calendar
from datetime import datetime
import json, os, decimal,re
from django.core.files import File
from itertools import chain
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
from .workers import Net, databaseobjects, Trialbalance, Ledgering, balanceSheet, Journalize
# Create your views here.


def index(request):
	p1 = Net(None,None)
	
	context = {"income": p1.netincome()[1],"expense":p1.netincome()[2],
		"netincome":p1.netincome()[0],"rawincome":p1.netincome()[3],"rawexpenses":p1.netincome()[4]}
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

			trial = Trialbalance()

			return render(request,"massage/trialbalance.html",trial.trialbalance(startdate,enddate))
		else:
			return render(request,"massage/trialbalance.html",context)
	else:
		return HttpResponseRedirect(reverse("index"))

def ledger(request):
	objects = databaseobjects()
	context = {"Journals": objects.alljournal(),"chart": objects.chartofaccs()}
	ledgering = Ledgering()
	if request.user.is_authenticated:

		if request.method == "POST":

				startdate = request.POST.get("startdate",False)

				enddate = request.POST.get("enddate",False)

				account = request.POST.get("account",False)

				return render(request,"massage/ledger.html",ledgering.ledgering(startdate,enddate,account))

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

			accounts = ('Current assets','Non-current assets','Current liabilities',
						'Non-current liabilities',"Owner's equity")
			accounts1 = ('Current assets','Non-current assets','Current liabilities',
						'Non-current liabilities',"Owner's equity")
			context = {}
			balance = balanceSheet()
			for x in accounts:
				context[x.replace(" ","").replace("-","").replace("'","")] = balance.balancing(startdate,enddate,x)

			for x in accounts1:
				context[x.replace(" ","").replace("-","").replace("'","")+"totals"] = balance.totals(startdate,enddate,x)

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

			startdate = request.POST.get("startdate",False)

			enddate = request.POST.get("enddate",False)

			p1 = Net(startdate,enddate)

			return render(request,"massage/incomestatement.html",p1.incomestatement())

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

	data1 = request.POST["json"]
	basedate = request.POST["basedate"]

	j = Journalize()
	context = {"status":j.journalInsert(data1,basedate)}
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