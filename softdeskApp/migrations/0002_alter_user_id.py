# Generated by Django 4.2.20 on 2025-03-08 00:52

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('softdeskApp', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='user',
            name='id',
            field=models.AutoField(primary_key=True, serialize=False),
        ),
    ]
