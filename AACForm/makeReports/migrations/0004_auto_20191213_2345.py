# Generated by Django 2.2.5 on 2019-12-14 05:45

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('makeReports', '0003_auto_20191213_2149'),
    ]

    operations = [
        migrations.AlterField(
            model_name='assessmentversion',
            name='frequency',
            field=models.CharField(max_length=500),
        ),
    ]
