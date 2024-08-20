# Generated by Django 4.2.2 on 2023-09-04 13:09

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('user', '0002_alter_userresume_display_name'),
    ]

    operations = [
        migrations.AddField(
            model_name='user',
            name='signup_type',
            field=models.CharField(choices=[('google', 'Google'), ('email', 'Email')], default='email', max_length=20),
        ),
    ]
