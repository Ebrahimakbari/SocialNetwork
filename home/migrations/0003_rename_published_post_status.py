# Generated by Django 5.1.3 on 2024-12-04 18:55

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('home', '0002_post_published'),
    ]

    operations = [
        migrations.RenameField(
            model_name='post',
            old_name='published',
            new_name='status',
        ),
    ]
