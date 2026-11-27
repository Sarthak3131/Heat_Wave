from django.db import migrations


def create_roles(apps, schema_editor):
    group_model = apps.get_model('auth', 'Group')
    group_model.objects.get_or_create(name='Administrator')
    group_model.objects.get_or_create(name='Regular User')


def remove_roles(apps, schema_editor):
    group_model = apps.get_model('auth', 'Group')
    group_model.objects.filter(name__in=['Administrator', 'Regular User']).delete()


class Migration(migrations.Migration):
    dependencies = [('auth', '0012_alter_user_first_name_max_length')]
    operations = [migrations.RunPython(create_roles, remove_roles)]
