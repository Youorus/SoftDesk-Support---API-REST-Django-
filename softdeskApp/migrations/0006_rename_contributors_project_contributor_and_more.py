# Generated by Django 4.2.20 on 2025-03-09 11:22

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('softdeskApp', '0005_project_contributors_alter_contributor_project'),
    ]

    operations = [
        migrations.RenameField(
            model_name='project',
            old_name='contributors',
            new_name='contributor',
        ),
        migrations.AlterUniqueTogether(
            name='contributor',
            unique_together=set(),
        ),
        migrations.AlterField(
            model_name='contributor',
            name='project',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='contributors', to='softdeskApp.project'),
        ),
        migrations.AddConstraint(
            model_name='contributor',
            constraint=models.UniqueConstraint(fields=('user', 'project'), name='unique_contributor'),
        ),
    ]
