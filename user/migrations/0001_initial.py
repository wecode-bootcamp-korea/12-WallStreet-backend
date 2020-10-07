# Generated by Django 3.1.2 on 2020-10-06 16:08

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Bank',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=30)),
            ],
            options={
                'db_table': 'banks',
            },
        ),
        migrations.CreateModel(
            name='BankAccount',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('account_number', models.CharField(max_length=200)),
                ('virtual_account_number', models.CharField(max_length=200)),
                ('balance', models.DecimalField(decimal_places=2, max_digits=15)),
                ('account_bank', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='account_bank', to='user.bank')),
                ('virtual_account_bank', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='virtual_account_bank', to='user.bank')),
            ],
            options={
                'db_table': 'bank_accounts',
            },
        ),
        migrations.CreateModel(
            name='User',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=50)),
                ('nickname', models.CharField(max_length=50)),
                ('email', models.EmailField(max_length=300)),
                ('password', models.EmailField(max_length=500)),
                ('is_active', models.BooleanField(default=False)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('bank_account', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='user.bankaccount')),
            ],
            options={
                'db_table': 'users',
            },
        ),
    ]
