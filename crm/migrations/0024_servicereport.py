# Generated by Django 5.1.4 on 2024-12-23 08:22

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('crm', '0023_personal_status'),
    ]

    operations = [
        migrations.CreateModel(
            name='ServiceReport',
            fields=[
            ],
            options={
                'verbose_name': 'Отчет по услугам',
                'proxy': True,
                'indexes': [],
                'constraints': [],
            },
            bases=('crm.appointment',),
        ),
    ]
