# Generated by Django 5.1.6 on 2025-03-05 21:08

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0018_user_is_mobile_user_alter_user_groups_and_more'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='employe',
            options={'verbose_name': 'Employé', 'verbose_name_plural': 'Employés'},
        ),
    ]
