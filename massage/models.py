from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.db import models, connection
from django.contrib.auth.models import User
from datetime import date
# Create your models here.

class chartofaccounts(models.Model):
	account_name = models.CharField(max_length=100)
	account_type = models.CharField(max_length=100)
	account_detailtype = models.CharField(max_length=100)
	account_description = models.CharField(max_length=250)
	account_balance = models.DecimalField(max_digits = 6, decimal_places = 2)

	def __str__(self):
		return f"Account Name: {self.account_name} | Account Type: {self.account_type} | Account Detailed Type: {self.account_detailtype} | Account Description: {self.account_description} | Account Balance: {self.account_balance}"

class service_category(models.Model):
	category_name = models.CharField(max_length=100)

	def __str__(self):
		return f"Category Name: {self.category_name}"
		
class serviceInfo(models.Model):
	service_name = models.CharField(max_length=100)
	service_sku = models.CharField(max_length=100)
	service_category =  models.ForeignKey(service_category,on_delete=models.PROTECT,null=True,related_name="service_category")
	service_description = models.CharField(max_length=100)
	service_price = models.DecimalField(max_digits = 6, decimal_places = 2)
	service_income_account = models.ForeignKey(chartofaccounts,on_delete=models.PROTECT,null=True,related_name="income_account")
	def __str__(self):
		return f"Service Name: {self.service_name} | Service Sku: {self.service_sku} | Service Category: {self.service_category} | Service Description: {self.service_description} | Service Price: {self.service_price} | Service Income Account: {self.service_income_account}"

class companyInfo(models.Model):

	company_name = models.CharField(max_length=100)
	company_phone = models.CharField(max_length=100)
	company_fax = models.CharField(max_length=100)
	company_country = models.CharField(max_length=100)
	company_city = models.CharField(max_length=100)
	company_state = models.CharField(max_length=100)
	company_zip = models.CharField(max_length=100)

	def __init__(self):
		return f"{self.company_name} | {self.company_phone} | {self.company_fax} | {self.company_country} | {self.company_city} | {self.company_state} | {self.company_zip}"

class journal(object):
	account_name = models.ForeignKey(chartofaccounts,on_delete=models.PROTECT,null=True,related_name="journal_account")
	pass