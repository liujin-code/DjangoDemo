# Generated by Django 4.1 on 2024-03-23 11:05

from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        ("boards", "0002_alter_post_updated_by"),
    ]

    operations = [
        migrations.RenameField(
            model_name="topic",
            old_name="start",
            new_name="starter",
        ),
    ]