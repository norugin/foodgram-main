# Generated by Django 5.1.6 on 2025-03-12 08:07

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('recipes', '0003_alter_recipe_author'),
    ]

    operations = [
        migrations.AddField(
            model_name='recipe',
            name='short_id',
            field=models.CharField(blank=True, max_length=10, null=True, unique=True),
        ),
    ]
