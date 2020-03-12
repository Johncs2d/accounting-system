# Generated by Django 3.0.3 on 2020-03-12 04:43

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('massage', '0009_auto_20200311_2215'),
    ]

    operations = [
        migrations.AlterField(
            model_name='chartofaccounts',
            name='account_credbalance',
            field=models.DecimalField(decimal_places=2, max_digits=12),
        ),
        migrations.AlterField(
            model_name='chartofaccounts',
            name='account_debbalance',
            field=models.DecimalField(decimal_places=2, max_digits=12),
        ),
        migrations.AlterField(
            model_name='journalcollections',
            name='credits',
            field=models.DecimalField(decimal_places=2, max_digits=12),
        ),
        migrations.AlterField(
            model_name='journalcollections',
            name='debits',
            field=models.DecimalField(decimal_places=2, max_digits=12),
        ),
        migrations.AlterField(
            model_name='journaltotals',
            name='account_credbalance',
            field=models.DecimalField(decimal_places=2, max_digits=12),
        ),
        migrations.AlterField(
            model_name='journaltotals',
            name='account_debbalance',
            field=models.DecimalField(decimal_places=2, max_digits=12),
        ),
        migrations.AlterField(
            model_name='logs',
            name='amount',
            field=models.DecimalField(decimal_places=2, max_digits=12),
        ),
        migrations.AlterField(
            model_name='logs',
            name='newbalance',
            field=models.DecimalField(decimal_places=2, max_digits=12),
        ),
        migrations.AlterField(
            model_name='serviceinfo',
            name='service_price',
            field=models.DecimalField(decimal_places=2, max_digits=12),
        ),
    ]