# Generated by Django 4.2.20 on 2025-03-10 20:18

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("softdeskApp", "0007_alter_comment_id_alter_issue_id_alter_project_id"),
    ]

    operations = [
        migrations.AlterField(
            model_name="user",
            name="age",
            field=models.PositiveIntegerField(editable=False),
        ),
    ]
