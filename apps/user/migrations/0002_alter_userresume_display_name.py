# Generated by Django 4.2.2 on 2023-08-10 14:26

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('user', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='userresume',
            name='display_name',
            field=models.CharField(max_length=155),
        ),
    ]
