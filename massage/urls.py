from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('info', views.info, name='info'),
    path('chart', views.charts, name='chart'),
    path('trialbalance', views.trialbalance, name='trialbalance'),
    path('ledger', views.ledger, name='ledger'),
    path('balancesheet', views.balancesheet, name='balancesheet'),
    path('incomestatement', views.incomestatement, name='incomestatement'),
    path('journalize', views.journalize, name='journalize'),
    path('sign_up/', views.sign_up, name='sign_up'),
    path("insertaccount", views.insertaccount, name='insertaccount'),
    path("inserjournal", views.inserjournal, name='inserjournal'),
    path("register", views.signupform, name='register'),
    path("login", views.loginForm, name='login'),
    path("logout", views.logusout, name='logout'),
    path("log_in", views.log_me_in, name='log_in'),
    path("journal_list", views.journalList, name='journal_list'),
    path("journal_control",views.journalControls,name='journalControls')
]