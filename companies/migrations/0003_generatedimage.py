# Generated by Django 4.2.2 on 2023-08-29 11:59

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('companies', '0002_room_message'),
    ]

    operations = [
        migrations.CreateModel(
            name='GeneratedImage',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('image', models.ImageField(upload_to='exports/charts/')),
                ('message', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='companies.message')),
            ],
        ),
    ]
