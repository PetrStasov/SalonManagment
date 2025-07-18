# Generated by Django 4.0 on 2024-12-10 12:02

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('crm', '0005_appointment'),
    ]

    operations = [
        migrations.CreateModel(
            name='Service',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=100)),
                ('duration', models.DurationField()),
                ('price', models.DecimalField(decimal_places=2, max_digits=10)),
                ('personal', models.ManyToManyField(to='crm.Personal')),
            ],
        ),
        migrations.DeleteModel(
            name='Communication',
        ),
    ]
