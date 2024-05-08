# Generated by Django 4.2.2 on 2023-11-05 11:50

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        (
            "miksi_apideck",
            "0002_remove_invoice_user_remove_room_company_delete_chat_and_more",
        ),
    ]

    operations = [
        migrations.CreateModel(
            name="UserInvoices",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("invoices_data", models.JSONField(default=dict)),
                (
                    "user",
                    models.OneToOneField(
                        on_delete=django.db.models.deletion.CASCADE,
                        to="miksi_apideck.usersignup",
                    ),
                ),
            ],
        ),
    ]