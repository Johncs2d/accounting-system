from django.shortcuts import render
from django.http import HttpResponse
# Create your views here.

def index(request):
	return render(request,"massage/index.html")


def info(request):
	return render(request,"massage/info.html")

def chartofaccounts(request):
	return render(request, "massage/chartsofaccounts.html")

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
	return render(request,"massage/journal.html")