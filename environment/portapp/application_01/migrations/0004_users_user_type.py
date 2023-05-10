# Generated by Django 4.0.7 on 2023-04-30 08:28

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('application_01', '0003_users_rollback'),
    ]

    operations = [
        migrations.AddField(
            model_name='users',
            name='user_type',
            field=models.CharField(choices=[('QUALITY', 'QUALITY'), ('LACHING', 'LACHING'), ('TRANSITOR', 'TRANSITOR'), ('COMEX', 'COMEX'), ('SUPER_COMEX', 'SUPER_COMEX')], default=None, max_length=20, null=True),
        ),
    ]