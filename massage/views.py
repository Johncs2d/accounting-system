from django.shortcuts import render
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from django.contrib.auth import login, authenticate, logout
from django.db import  IntegrityError
from django.utils.html import strip_tags
from django.urls import reverse
from django.contrib.auth.models import User
from .models import chartofaccounts, service_category, serviceInfo, companyInfo, journalmain, journalcollections, employees, logs
import  decimal
from django.views.decorators.csrf import csrf_exempt
from .workers import Net, databaseobjects, Trialbalance, Ledgering, balanceSheet, Journalize
# Create your views here.


def index(request):
	if request.user.is_authenticated:
		p1 = Net()
		context = {
			"income": p1.netincome()[1],
			"expense":p1.netincome()[2],
			"netincome":p1.netincome()[0],
			"rawincome":p1.netincome()[3],
			"rawexpenses":p1.netincome()[4]}
		return render(request,"massage/index.html",context)

	else:
		return render(request, "landingpage/index.html")

def signupform(request):
	if request.user.is_authenticated:
		return HttpResponseRedirect(reverse("index"))
	else:
		return render(request, "formpage/index.html")

def loginForm(request):
	if request.user.is_authenticated:
		return HttpResponseRedirect(reverse("index"))
	else:
		return render(request, "formpage/login.html")

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

		add = chartofaccounts(
			account_number=accountnumber,
			account_name=accountname,
			account_type=accountType,
			account_detailtype=accountDetail,
			account_debbalance=0.00,
			account_credbalance=0.00
		)

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

	if request.user.is_authenticated:
		context = {"chart": chartofaccounts.objects.all()}
		if request.method == "POST":

			startdate = request.POST.get("startdate",False)

			enddate = request.POST.get("enddate",False)

			account = request.POST.get("account",False)

			return render(
				request,
				"massage/ledger.html",
				Ledgering().ledgering(startdate,enddate,account)
			)

		else:
			return render(request,"massage/ledger.html",context)
	else:
		return HttpResponseRedirect(reverse("index"))


def balancesheet(request):

	if request.user.is_authenticated:

		if request.method == "POST":

			context = {}

			startdate = request.POST.get("startdate",False)

			enddate = request.POST.get("enddate",False)

			accounts = ('Current assets','Non-current assets','Current liabilities',
						'Non-current liabilities',"Owner's equity")

			#This seems like a bad idea but it's fine for now.
			for x in accounts:
				context[
					x.replace(" ","").replace("-","").replace("'","")
				] = balanceSheet().balancing(startdate,enddate,x)

			for x in accounts:
				context[
					x.replace(" ","").replace("-","").replace("'","")+"totals"
				] = balanceSheet().totals(startdate,enddate,x)

			context["totalasset"] = decimal.Decimal(context['Currentassetstotals']) + \
			decimal.Decimal(context['Noncurrentassetstotals'])

			context["totalliabilities"] = decimal.Decimal(context['Noncurrentliabilitiestotals']) + \
			decimal.Decimal(context['Currentliabilitiestotals'])

			context["totalliabilitesandequity"] = (decimal.Decimal(context['Noncurrentliabilitiestotals']) + \
				decimal.Decimal(context['Currentliabilitiestotals']))+(decimal.Decimal(context['Ownersequitytotals']))

			return render(request,"massage/balancesheet.html",context)

		else:
			return render(request,"massage/balancesheet.html")
	else:
		return HttpResponseRedirect(reverse("index"))


def incomestatement(request):

	if request.user.is_authenticated:

		if request.method == "POST":

			startdate = request.POST.get("startdate",False)

			enddate = request.POST.get("enddate",False)

			p1 = Net(startdate,enddate)

			return render(request,"massage/incomestatement.html",p1.incomestatement())

		else:
			return render(request,"massage/incomestatement.html")

	else:
		return HttpResponseRedirect(reverse("index"))

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

	context = {"status":Journalize().journalInsert(data1,basedate)}
	return JsonResponse(context)


	#SIGNUP
def sign_up(request):

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
				# user1 = authenticate(request, username=username, password=password)
				login(request, user)
				return HttpResponseRedirect(reverse("index"))
			except IntegrityError:
				pass
		else:
			return HttpResponseRedirect(reverse("signupform"))

def log_me_in(request):

	if request.method == "POST":
		username = strip_tags(request.POST["username"])
		password = strip_tags(request.POST["password"])

		user = authenticate(request, username=username, password=password)
		if user:
			login(request, user)
			return HttpResponseRedirect(reverse("index"))
		else:
			return render(request,"formpage/login.html",{"msg":"Incorrect Username or Password"})

	else:
		return HttpResponseRedirect(reverse("login"))

def logusout(request):
	if request.user.is_authenticated:
		logout(request)
		return HttpResponseRedirect(reverse("login"))
	else:
		return HttpResponseRedirect(reverse("login"))


def journalList(request):

	if request.user.is_authenticated:
		context = {"journ": journalcollections.objects.all(),"accounts":chartofaccounts.objects.all()}

		if request.method == "POST":
			startdate = request.POST.get("startdate",False)

			enddate = request.POST.get("enddate",False)
	
			return render(request,"massage/journals.html",context)
		else:
			
			return render(request,"massage/journals.html",context)
	else:
		return HttpResponseRedirect(reverse("index"))
@csrf_exempt
def journalControls(request):
	if request.method == "POST":
		objectId = request.POST.get('id',False)
		if request.POST.get("for",False) == "DELETION":
			
			b = journalcollections.objects.get(pk = objectId)
			b.delete()
			return HttpResponse("TRUE")

		elif request.POST.get("for",False) == "GETDATA":
			b = journalcollections.objects.get(pk = objectId)
			context = {"account":b.account_id.id,"debits":b.debits,"credits":b.credits,"description":b.description,
			"date":b.transaction_date.strftime('%Y-%m-%d')}
			return JsonResponse(context)

		else:
			c = chartofaccounts.objects.get(pk=request.POST.get("acctype",False))

			journalcollections.objects.filter(pk=objectId).update(

				transaction_date=request.POST.get("date",False),
				account_id=c,
				debits=request.POST.get("debits",0.00),
				credits=request.POST.get("credits",0.00),
				description=request.POST.get("desc",0.00)
				)
			return HttpResponse("TRUE")
	else:
		pass