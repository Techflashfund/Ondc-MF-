# Generated by Django 5.2 on 2025-05-13 08:44

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('ondc', '0005_submissionid'),
    ]

    operations = [
        migrations.CreateModel(
            name='SIPFulfillment',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('fulfillment_id', models.CharField(max_length=100)),
                ('scheme_name', models.CharField(max_length=255)),
                ('customer_id', models.CharField(max_length=50)),
                ('agent_id', models.CharField(blank=True, max_length=50, null=True)),
                ('investment_amount', models.PositiveIntegerField()),
                ('frequency', models.CharField(max_length=50)),
                ('schedule_str', models.TextField()),
                ('thresholds', models.JSONField()),
                ('submission_id', models.CharField(blank=True, max_length=100, null=True)),
                ('raw_payload', models.JSONField()),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('transaction', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='ondc.transaction')),
            ],
        ),
    ]
