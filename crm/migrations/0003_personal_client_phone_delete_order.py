# Generated by Django 4.2.17 on 2024-12-08 17:51

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('crm', '0002_alter_client_options_alter_client_birth_date_and_more'),
    ]

    operations = [
        migrations.CreateModel(
            name='Personal',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('full_name', models.CharField(max_length=200, verbose_name='ФИО')),
                ('post', models.CharField(max_length=200, verbose_name='Должность')),
                ('date_of_employment', models.DateField(verbose_name='Дата приема')),
            ],
        ),
        migrations.AddField(
            model_name='client',
            name='phone',
            field=models.CharField(default='', max_length=11, verbose_name='Телефон'),
        ),
        migrations.DeleteModel(
            name='Order',
        ),
    ]
