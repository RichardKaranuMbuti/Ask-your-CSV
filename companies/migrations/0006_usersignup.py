# Generated by Django 4.2.2 on 2023-07-05 09:18

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('companies', '0005_rename_status_apikey_active_company_active'),
    ]

    operations = [
        migrations.CreateModel(
            name='UserSignup',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('first_name', models.CharField(max_length=50)),
                ('last_name', models.CharField(max_length=50)),
                ('email', models.EmailField(max_length=100)),
            ],
        ),
    ]