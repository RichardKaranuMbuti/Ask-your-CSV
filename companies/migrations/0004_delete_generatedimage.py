# Generated by Django 4.2.2 on 2023-09-11 07:32

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('companies', '0003_generatedimage'),
    ]

    operations = [
        migrations.DeleteModel(
            name='GeneratedImage',
        ),
    ]