# Generated by Django 5.2 on 2025-05-13 09:41

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('ondc', '0009_alter_submissionid_message_id'),
    ]

    operations = [
        migrations.AlterField(
            model_name='submissionid',
            name='message_id',
            field=models.CharField(blank=True, default='123', max_length=100, null=True),
        ),
    ]
