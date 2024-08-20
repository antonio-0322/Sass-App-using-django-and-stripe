# Generated by Django 4.2.2 on 2023-08-01 05:30

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('payment', '0001_initial'),
        ('job_applying', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='appliedjob',
            name='used_subscription',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='applied_jobs', to='payment.subscription'),
        ),
    ]
