# Generated by Django 5.2 on 2025-05-12 11:43

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('ondc', '0003_delete_fullonselect'),
    ]

    operations = [
        migrations.CreateModel(
            name='SelectSIP',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('message_id', models.CharField(max_length=100)),
                ('payload', models.JSONField()),
                ('timestamp', models.DateTimeField()),
                ('transaction', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='full_on_selects', to='ondc.transaction')),
            ],
        ),
    ]
