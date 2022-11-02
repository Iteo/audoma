# Generated by Django 4.1.2 on 2022-10-26 08:32

import django.db.models.deletion
from django.db import (
    migrations,
    models,
)

import audoma.django.db.fields


class Migration(migrations.Migration):

    dependencies = [
        ("audoma_api", "0005_auto_20220706_1013"),
    ]

    operations = [
        migrations.CreateModel(
            name="CarTag",
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
                ("name", audoma.django.db.fields.CharField(max_length=255)),
                (
                    "car",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="tags",
                        to="audoma_api.car",
                    ),
                ),
            ],
        ),
    ]