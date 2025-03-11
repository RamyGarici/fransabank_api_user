from django.db import migrations

def create_groups(apps, schema_editor):
    Group = apps.get_model('auth', 'Group')
    Group.objects.get_or_create(name="Admin")
    Group.objects.get_or_create(name="Agent")

class Migration(migrations.Migration):
    dependencies = [
        ('api', '0010_typedocument_deleted_at'), 
    ]

    operations = [
        migrations.RunPython(create_groups),
    ]