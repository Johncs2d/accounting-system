from django.urls import path

from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('info', views.info, name='info'),
    path('chart', views.chartofaccounts, name='chart'),
    path('trialbalance', views.trialbalance, name='trialbalance'),
    path('ledger', views.ledger, name='ledger'),
    path('balancesheet', views.balancesheet, name='balancesheet'),
    path('incomestatement', views.incomestatement, name='incomestatement'),
    path('receive', views.receive, name='receive'),
    path('journalize', views.journalize, name='journalize'),
]