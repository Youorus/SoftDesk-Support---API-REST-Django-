# Generated by Django 4.2.20 on 2025-03-08 14:38

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('softdeskApp', '0003_alter_contributor_id_alter_user_id'),
    ]

    operations = [
        migrations.AlterField(
            model_name='contributor',
            name='role',
            field=models.CharField(choices=[('contributor', 'Contributor'), ('author', 'Author')], default='contributor', max_length=20),
        ),
    ]
