# Generated by Django 5.2 on 2025-05-16 04:26

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('ondc', '0012_onconfirm'),
    ]

    operations = [
        migrations.CreateModel(
            name='OnStatus',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('message_id', models.CharField(max_length=100)),
                ('payload', models.JSONField()),
                ('timestamp', models.DateTimeField()),
                ('transaction', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='full_on_status', to='ondc.transaction')),
            ],
        ),
        migrations.CreateModel(
            name='OnUpdate',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('message_id', models.CharField(max_length=100)),
                ('payload', models.JSONField()),
                ('timestamp', models.DateTimeField()),
                ('transaction', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='full_on_update', to='ondc.transaction')),
            ],
        ),
    ]
