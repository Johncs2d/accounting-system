from django.contrib import admin
from .models import chartofaccounts, service_category, serviceInfo, companyInfo, journalmain, journalcollections, employees, logs, journalTotals

admin.site.site_header = 'Tranquil Touch'
admin.site.site_title = 'Tranquil Touch'


class journalInlines(admin.TabularInline):
	model = journalcollections
	
class journaladmin(admin.ModelAdmin):
    inlines = [journalInlines]
# Register your models here.
admin.site.register(chartofaccounts)
admin.site.register(journalmain,journaladmin)
admin.site.register(journalTotals)
admin.site.register(journalcollections)