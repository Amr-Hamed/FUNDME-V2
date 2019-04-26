# Generated by Django 2.1 on 2019-04-26 03:04

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('userProfile', '0002_userprofile_email'),
    ]

    operations = [
        migrations.AlterField(
            model_name='userprofile',
            name='email',
            field=models.EmailField(default='d@gmail.com', max_length=254, unique=True, verbose_name='email address'),
        ),
    ]