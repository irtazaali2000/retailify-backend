# Generated by Django 3.0.4 on 2024-04-03 12:00

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('product', '0007_auto_20240402_1043'),
    ]

    operations = [
        migrations.AlterField(
            model_name='image',
            name='image_url',
            field=models.TextField(blank=True),
        ),
    ]
