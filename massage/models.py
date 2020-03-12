from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.db import models, connection
from django.contrib.auth.models import User
from datetime import date
# Create your models here.

class chartofaccounts(models.Model):
	typeschoices = (
		("Current assets", "Current assets"),
		("Fixed assets", "Fixed assets"),
		("Non-current assets", "Non-current assets"),
		("Current liabilities", "Current liabilities"),
		("Non-current liabilities", "Non-current liabilities"),
		("Owner's equity", "Owner's equity"),
		("Expenses", "Expenses"),
		("Income", "Income"),)
	account_number = models.IntegerField(unique=True)
	account_name = models.CharField(max_length=100,unique=True)
	account_type = models.CharField(max_length=100,choices = typeschoices)
	account_detailtype = models.CharField(max_length=100)
	account_debbalance = models.DecimalField(max_digits = 12, decimal_places = 2)
	account_credbalance = models.DecimalField(max_digits = 12, decimal_places = 2)

	def __str__(self):
		return f"Account Number: {self.account_number} | Account Name: {self.account_name} | Account Type: {self.account_type} | \
				Account Detailed Type: {self.account_detailtype}  \
				| Account Debit Balance: {self.account_debbalance} | Account Credit Balance: {self.account_credbalance}"

class service_category(models.Model):
	category_name = models.CharField(max_length=100)

	def __str__(self):
		return f"Category Name: {self.category_name}"
		
class serviceInfo(models.Model):
	service_name = models.CharField(max_length=100)
	service_sku = models.CharField(max_length=100)
	service_category =  models.ForeignKey(service_category,on_delete=models.PROTECT,null=True, 
											related_name="service_category")
	service_description = models.CharField(max_length=100)
	service_price = models.DecimalField(max_digits = 12, decimal_places = 2)
	service_income_account = models.ForeignKey(chartofaccounts,on_delete=models.PROTECT,
		null=False,related_name="income_account")
	def __str__(self):
		return f"Service Name: {self.service_name} | Service Sku: {self.service_sku} | \
				Service Category: {self.service_category} | Service Description: {self.service_description} | \
				Service Price: {self.service_price} | Service Income Account: {self.service_income_account}"

class companyInfo(models.Model):

	company_name = models.CharField(max_length=100)
	company_phone = models.CharField(max_length=100)
	company_fax = models.CharField(max_length=100)
	company_country = models.CharField(max_length=100)
	company_city = models.CharField(max_length=100)
	company_state = models.CharField(max_length=100)
	company_zip = models.CharField(max_length=100)

	def __str__(self):
		return f"{self.company_name} | {self.company_phone} | {self.company_fax} | \
				{self.company_country} | {self.company_city} | {self.company_state} | {self.company_zip}"

class journalmain(models.Model):
	datecreated = models.DateField(("Date"), default=date.today)
	def __str__(self):
		return f"Journal ID {self.pk} | Date Created {self.datecreated}"
		
class journalcollections(models.Model):
	transaction_date = models.DateField(("Date"), null=False)
	account_id = models.ForeignKey(chartofaccounts,on_delete=models.PROTECT,null=True,
									related_name="journal_account")
	debits = models.DecimalField(max_digits = 12, decimal_places = 2)
	credits = models.DecimalField(max_digits = 12, decimal_places = 2)
	description = models.CharField(max_length=200)
	journalid = models.ForeignKey(journalmain,on_delete=models.PROTECT,null=False,related_name="journals")
	def __str__(self):
		return f"{self.transaction_date} | {self.account_id}  | $ {self.debits} | $ \
				{self.credits} | {self.description} | Journal #{self.journalid.id} "



class employees(models.Model):
	employee_name = models.CharField(max_length=100)
	employee_city = models.CharField(max_length=100)
	employee_status = models.CharField(max_length=20)
	employee_position = models.CharField(max_length=20)
	def __str__(self):
		return f"{self.employee_name} | {self.employee_city} | {self.employee_status} | {self.employee_position}"

class logs(models.Model):
	event_name = models.CharField(max_length=100)
	account_involved = models.ForeignKey(chartofaccounts,on_delete=models.PROTECT,
										null=True,related_name="logs_account")
	amount = models.DecimalField(max_digits = 12, decimal_places = 2)
	newbalance = models.DecimalField(max_digits = 12, decimal_places = 2)
	date = models.DateField(("Date"), default=date.today)
	def __str__(self):
		return f"{self.event_name} | {self.account_involved} | {self.amount} | {self.newbalance} | {self.date}"

class journalTotals(models.Model):
	journalid = models.ForeignKey(journalmain,on_delete=models.PROTECT,null=False,related_name="journalsmain")
	account_id = models.ForeignKey(chartofaccounts,on_delete=models.PROTECT,null=True,
									related_name="totals_account")
	account_number = models.IntegerField()
	account_debbalance = models.DecimalField(max_digits = 12, decimal_places = 2)
	account_credbalance = models.DecimalField(max_digits = 12, decimal_places = 2)
	def __str__(self):
		return f"{self.journalid.id} || {self.account_id.account_number} || {self.account_number} || {self.account_debbalance} || {self.account_credbalance}"
		